import json
import os
import time
from typing import List, Dict, Any, Tuple, Callable

import cv2
from ultralytics import YOLO

from .config import settings
from .tracker import SimpleCentroidTracker
from .utils.geometry import bbox_center, bbox_iou, bbox_polygon_intersect


CLASS_NAMES = ["Cat", "Person", "Dog", "Knife", "Fire", "Smoke", "Door/Window", "Crowbar"]


class YoloSecurityService:
    """
    封装 YOLO 推理+业务告警逻辑

      视频帧采集与预处理
      YOLOv11n 自定义模型推理输出目标框
      基于规则的异常事件判断（火/烟、刀具移动、门窗入侵、禁区入侵）
      叠加可视化标注，并在触发时生成事件记录
    """

    def __init__(self):
        model_path = settings.model_path
        if not os.path.exists(model_path):
            # 兼容从 backend/ 启动时的相对路径
            alt = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", model_path))
            if os.path.exists(alt):
                model_path = alt
        self.model = YOLO(model_path)
        self.weapon_tracker = SimpleCentroidTracker()
        self.person_intrusion_tracker = SimpleCentroidTracker(
            max_missing=settings.person_track_max_missing,
            match_iou=settings.person_track_match_iou,
        )
        # tid -> {"inside_streak": int, "armed": bool}，门窗与ROI各一套状态
        self._door_intrusion_track_state: Dict[int, Dict[str, Any]] = {}
        self._roi_intrusion_track_state: Dict[int, Dict[str, Any]] = {}
        self.last_alarm_at = {}  # alarm_type -> timestamp
        # Fire/Smoke：按类别分别维护同区域连续检测计数
        self._fire_smoke_track = {
            "Fire": {"streak": 0, "bbox": None},
            "Smoke": {"streak": 0, "bbox": None},
        }

    def _cooldown_ok(self, alarm_type: str) -> bool:
        now = time.time()
        last = self.last_alarm_at.get(alarm_type, 0.0)
        if now - last >= settings.alarm_cooldown_sec:
            self.last_alarm_at[alarm_type] = now
            return True
        return False

    def _step_fire_smoke_streak(self, cls_name: str, dets: List[Dict[str, Any]]) -> bool:
        """
        更新 Fire/Smoke的同区域连续计数；本帧若已达N帧则返回True(外层再结合cooldown决定是否告警)。
        达到阈值后若因冷却未落库，保持 streak 不清零，直至成功告警后由外层重置。
        """
        if cls_name not in self._fire_smoke_track:
            return False
        min_conf = float(settings.fire_smoke_conf_thres)
        need = int(settings.fire_smoke_consecutive_frames)
        iou_min = float(settings.fire_smoke_region_iou_min)
        cand = [d for d in dets if d["cls_name"] == cls_name and float(d["conf"]) >= min_conf]
        st = self._fire_smoke_track[cls_name]

        if not cand:
            st["streak"] = 0
            st["bbox"] = None
            return False

        prev = st["bbox"]
        if prev is None:
            best = max(cand, key=lambda x: float(x["conf"]))
            st["bbox"] = list(best["bbox"])
            st["streak"] = 1
            return need <= 1

        best_iou = -1.0
        best_det = None
        for d in cand:
            iou = bbox_iou(prev, d["bbox"])
            if iou > best_iou:
                best_iou = iou
                best_det = d

        if best_iou >= iou_min:
            if st["streak"] < need:
                st["streak"] += 1
            st["bbox"] = list(best_det["bbox"])
        else:
            best = max(cand, key=lambda x: float(x["conf"]))
            st["streak"] = 1
            st["bbox"] = list(best["bbox"])

        return st["streak"] >= need

    def infer(self, frame_bgr) -> Tuple[Any, List[Dict[str, Any]]]:
        """
        返回：annotated_frame, detections
        detections 格式：
          [{
            cls_name, conf, bbox[x1,y1,x2,y2], track_id?
          }, ...]
        """
        res = self.model.predict(
            source=frame_bgr,
            conf=settings.conf_thres,
            iou=settings.iou_thres,
            verbose=False,
        )[0]

        dets = []
        if res.boxes is not None and len(res.boxes) > 0:
            for b in res.boxes:
                cls_id = int(b.cls.item())
                conf = float(b.conf.item())
                x1, y1, x2, y2 = [float(v) for v in b.xyxy[0].tolist()]
                cls_name = CLASS_NAMES[cls_id] if 0 <= cls_id < len(CLASS_NAMES) else str(cls_id)
                dets.append(
                    {"cls_id": cls_id, "cls_name": cls_name, "conf": conf, "bbox": [x1, y1, x2, y2]}
                )

        # 给Knife/Crowbar做追踪，用于“移动告警”
        weapon_dets = [d for d in dets if d["cls_name"] in ("Knife", "Crowbar")]
        weapon_dets = self.weapon_tracker.update(weapon_dets)
        weapon_map = {(d["cls_name"], tuple(d["bbox"])): d.get("track_id") for d in weapon_dets}
        for d in dets:
            if d["cls_name"] in ("Knife", "Crowbar"):
                d["track_id"] = weapon_map.get((d["cls_name"], tuple(d["bbox"])))

        person_dets = [d for d in dets if d["cls_name"] == "Person"]
        self.person_intrusion_tracker.update(person_dets)

        annotated = self._draw(frame_bgr.copy(), dets)
        return annotated, dets

    def evaluate_alarms(self, dets: List[Dict[str, Any]], frame_shape_hw) -> List[Dict[str, Any]]:
        """
        执行业务规则，输出本帧触发的告警列表。
        """
        alarms = []

        # 1) Fire/Smoke：更高置信度+同一区域连续N帧才告警（降低误报）
        if self._step_fire_smoke_streak("Fire", dets) and self._cooldown_ok("Fire"):
            alarms.append(
                {
                    "alarm_type": "Fire",
                    "level": "HIGH",
                    "message": "检测到火灾风险（Fire，已连续同区域多帧高置信度确认）",
                }
            )
            self._fire_smoke_track["Fire"]["streak"] = 0
            self._fire_smoke_track["Fire"]["bbox"] = None
        if self._step_fire_smoke_streak("Smoke", dets) and self._cooldown_ok("Smoke"):
            alarms.append(
                {
                    "alarm_type": "Smoke",
                    "level": "HIGH",
                    "message": "检测到烟雾风险（Smoke，已连续同区域多帧高置信度确认）",
                }
            )
            self._fire_smoke_track["Smoke"]["streak"] = 0
            self._fire_smoke_track["Smoke"]["bbox"] = None

        # 2) Knife/Crowbar：必须发生明显移动才告警
        #    判定方法：同一 track_id在连续帧的中心点位移（像素）超过阈值
        #    为什么这样设计：
        #    - 画面里静止刀具不一定是威胁（可能是厨房台面）
        #    - 通过位移阈值把“静止物体”与“疑似持械移动/挥动”区分开
        for d in dets:
            if d["cls_name"] not in ("Knife", "Crowbar"):
                continue
            tid = d.get("track_id")
            if not tid:
                continue
            disp = self.weapon_tracker.get_displacement_px(tid)
            if disp >= settings.weapon_move_px_thres:
                at = f"WeaponMove_{d['cls_name']}"
                if self._cooldown_ok(at):
                    alarms.append(
                        {
                            "alarm_type": "WeaponMove",
                            "level": "MEDIUM",
                            "message": f"{d['cls_name']} 出现危险移动（位移 {disp:.1f}px/帧）",
                            "weapon": d["cls_name"],
                            "track_id": tid,
                            "displacement_px": disp,
                        }
                    )

        # 3) 异常闯入
        doors = [d for d in dets if d["cls_name"] == "Door/Window"]

        # 机制A：门窗入侵（时序：先进入敏感区并停留，再离开或连续丢检才告警）
        alarms.extend(self._evaluate_door_intrusion(doors))

        # 机制 B：禁区闯入（多边形禁区，与门窗相同算法）
        roi = settings.roi_polygon or []
        if isinstance(roi, list) and len(roi) >= 3:
            h, w = frame_shape_hw
            poly_px = [(float(x) * w, float(y) * h) for x, y in roi]
            alarms.extend(self._evaluate_roi_intrusion(poly_px))
        else:
            self._prune_stale_intrusion_track_state(self._roi_intrusion_track_state)

        return alarms

    def _person_intersects_any_door(self, pb: List[float], doors: List[Dict[str, Any]]) -> bool:
        if not doors:
            return False
        pcx, pcy = bbox_center(pb)
        for dw in doors:
            db = dw["bbox"]
            iou = bbox_iou(pb, db)
            center_inside = (db[0] <= pcx <= db[2]) and (db[1] <= pcy <= db[3])
            if iou > settings.door_iou_thres or center_inside:
                return True
        return False

    def _prune_stale_intrusion_track_state(self, track_state: Dict[int, Dict[str, Any]]) -> None:
        active = set(self.person_intrusion_tracker.tracks.keys())
        for tid in list(track_state.keys()):
            if tid not in active:
                del track_state[tid]

    def _evaluate_temporal_intrusion(
        self,
        track_state: Dict[int, Dict[str, Any]],
        zone_active: bool,
        in_zone_fn: Callable[[List[float]], bool],
        cooldown_key: str,
        mode: str,
        message_leave: str,
        message_disappear: str,
    ) -> List[Dict[str, Any]]:
        """
        通用时序闯入：先连续若干帧在敏感区内，再离开敏感区或连续丢检才告警。
        """
        alarms: List[Dict[str, Any]] = []
        if not zone_active:
            self._prune_stale_intrusion_track_state(track_state)
            return alarms

        need_dwell = int(settings.door_intrusion_min_dwell_frames)
        need_missing = int(settings.door_intrusion_disappear_missing_frames)

        active_tids = set(self.person_intrusion_tracker.tracks.keys())
        for tid in list(track_state.keys()):
            if tid not in active_tids:
                del track_state[tid]

        for tid, tr in self.person_intrusion_tracker.tracks.items():
            missing = int(tr["missing"])
            bbox = tr["bbox"]
            st = track_state.setdefault(tid, {"inside_streak": 0, "armed": False})

            in_zone = in_zone_fn(bbox)

            if missing == 0:
                if in_zone:
                    st["inside_streak"] = st.get("inside_streak", 0) + 1
                    if st["inside_streak"] >= need_dwell:
                        st["armed"] = True
                else:
                    if st.get("armed"):
                        if self._cooldown_ok(cooldown_key):
                            alarms.append(
                                {
                                    "alarm_type": "Intrusion",
                                    "level": "HIGH",
                                    "message": message_leave,
                                    "mode": mode,
                                    "intrusion_event": "leave",
                                    "track_id": tid,
                                }
                            )
                        st["armed"] = False
                        st["inside_streak"] = 0
                    else:
                        st["inside_streak"] = 0
            else:
                if st.get("armed") and missing >= need_missing:
                    if self._cooldown_ok(cooldown_key):
                        alarms.append(
                            {
                                "alarm_type": "Intrusion",
                                "level": "HIGH",
                                "message": message_disappear,
                                "mode": mode,
                                "intrusion_event": "disappear",
                                "track_id": tid,
                            }
                        )
                    st["armed"] = False
                    st["inside_streak"] = 0
                elif not st.get("armed"):
                    st["inside_streak"] = 0

        return alarms

    def _evaluate_door_intrusion(self, doors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        门窗入侵：人员须先在门/窗检测框敏感区内连续停留若干帧，
        之后在仍被跟踪时离开敏感区，或连续多帧未检测到该人，才触发告警。
        """
        return self._evaluate_temporal_intrusion(
            self._door_intrusion_track_state,
            zone_active=bool(doors),
            in_zone_fn=lambda b: self._person_intersects_any_door(b, doors),
            cooldown_key="Intrusion_Door",
            mode="Door/Window",
            message_leave="疑似门窗非法闯入（时序：人员曾进入门窗敏感区后离开该区域）",
            message_disappear="疑似门窗非法闯入（时序：人员在门窗附近后连续丢检，疑似穿过或离开视场）",
        )

    def _evaluate_roi_intrusion(self, poly_px: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
        """ROI 禁区闯入，规则与门窗时序一致。"""
        return self._evaluate_temporal_intrusion(
            self._roi_intrusion_track_state,
            zone_active=len(poly_px) >= 3,
            in_zone_fn=lambda b: bbox_polygon_intersect(b, poly_px),
            cooldown_key="Intrusion_ROI",
            mode="ROI",
            message_leave="检测到禁区闯入（时序：人员曾进入禁区后离开该区域）",
            message_disappear="检测到禁区闯入（时序：人员在禁区附近后连续丢检，疑似穿过或离开视场）",
        )

    def _draw(self, frame_bgr, dets: List[Dict[str, Any]]):
        """
        绘制检测框与标签
        """
        for d in dets:
            x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
            cls = d["cls_name"]
            conf = d["conf"]
            color = (0, 255, 0)
            if cls in ("Fire", "Smoke"):
                color = (0, 0, 255)
            if cls in ("Knife", "Crowbar"):
                color = (0, 165, 255)
            if cls == "Door/Window":
                color = (255, 255, 0)
            cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), color, 2)
            tid = d.get("track_id")
            tag = f"{cls} {conf:.2f}" + (f" id:{tid}" if tid else "")
            cv2.putText(
                frame_bgr,
                tag,
                (x1, max(20, y1 - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
                cv2.LINE_AA,
            )
        return frame_bgr

