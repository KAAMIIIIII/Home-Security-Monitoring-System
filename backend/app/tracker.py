from typing import Dict, Tuple
from .utils.geometry import bbox_center, bbox_iou


class SimpleCentroidTracker:
    """
    刀具/撬棍移动追踪器（给刀具/撬棍移动告警提供连续帧ID）

    设计目的：
    家庭监控对象环境存在用户长时间放置刀具/撬棍的情况，需要追踪器来判断刀具/撬棍是否在移动。

    核心做法：
      对每帧同类别目标，用IoU与上一帧目标做匹配，匹配到则沿用ID
      未匹配到的目标分配新ID
      目标消失则计数，超过一定帧数删除
    """

    def __init__(self, max_missing: int = 8, match_iou: float = 0.2):
        self.next_id = 1
        self.tracks: Dict[int, dict] = {}
        self.max_missing = max_missing
        self.match_iou = match_iou

    def update(self, dets):
        """
        dets: list of dict, each dict contains:
          - cls_name
          - bbox: [x1,y1,x2,y2]

        返回：为每个det添加track_id字段
        """
        # 先把所有 track missing+1
        for tid in list(self.tracks.keys()):
            self.tracks[tid]["missing"] += 1
            if self.tracks[tid]["missing"] > self.max_missing:
                del self.tracks[tid]

        results = []
        for det in dets:
            cls_name = det["cls_name"]
            bbox = det["bbox"]
            best_tid = None
            best_iou = 0.0
            for tid, tr in self.tracks.items():
                if tr["cls_name"] != cls_name:
                    continue
                iou = bbox_iou(bbox, tr["bbox"])
                if iou > best_iou:
                    best_iou = iou
                    best_tid = tid

            if best_tid is not None and best_iou >= self.match_iou:
                # 匹配成功：更新轨迹
                prev_center = self.tracks[best_tid]["center"]
                new_center = bbox_center(bbox)
                self.tracks[best_tid].update(
                    {
                        "bbox": bbox,
                        "center": new_center,
                        "missing": 0,
                        "prev_center": prev_center,
                    }
                )
                det["track_id"] = best_tid
            else:
                # 新目标：分配新ID
                tid = self.next_id
                self.next_id += 1
                c = bbox_center(bbox)
                self.tracks[tid] = {
                    "cls_name": cls_name,
                    "bbox": bbox,
                    "center": c,
                    "prev_center": c,
                    "missing": 0,
                }
                det["track_id"] = tid

            results.append(det)
        return results

    def get_displacement_px(self, track_id: int) -> float:
        """
        返回该track在“上一帧 ->当前帧”的中心点位移像素
        """
        tr = self.tracks.get(track_id)
        if not tr:
            return 0.0
        (x1, y1) = tr.get("prev_center", tr["center"])
        (x2, y2) = tr["center"]
        dx = x2 - x1
        dy = y2 - y1
        return (dx * dx + dy * dy) ** 0.5

