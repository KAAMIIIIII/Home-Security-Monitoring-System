import asyncio
import json
import time
import cv2

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ..config import settings
from ..yolo_service import YoloSecurityService
from ..utils.image import bgr_to_jpeg_base64, save_event_image
from ..db import SessionLocal
from ..models import Event


router = APIRouter(tags=["stream"])

_service = None


def get_service() -> YoloSecurityService:
    global _service
    if _service is None:
        _service = YoloSecurityService()
    return _service


def _open_capture():
    """
    打开视频源：
    - settings.video_source == "0"/"1" 等：本机摄像头索引
    - 否则当作 URL（RTSP/HTTP）
    """
    src = settings.video_source
    if isinstance(src, str) and src.isdigit():
        cap = cv2.VideoCapture(int(src))
    else:
        cap = cv2.VideoCapture(src)
    return cap


@router.websocket("/api/video/stream")
async def video_stream(ws: WebSocket):
    await ws.accept()
    cap = _open_capture()
    svc = get_service()
    db: Session = SessionLocal()

    try:
        if not cap.isOpened():
            await ws.send_text(json.dumps({"type": "error", "message": "无法打开摄像头/视频源"}))
            return

        last_send = 0.0
        fps_limit = 15.0  # 控制推流频率，避免前端卡顿

        while True:
            # 允许前端随时发消息（例如未来扩展：切换源/暂停）
            try:
                _ = await asyncio.wait_for(ws.receive_text(), timeout=0.001)
            except Exception:
                pass

            ok, frame = cap.read()
            if not ok:
                await asyncio.sleep(0.05)
                continue

            # 端到端延迟起点：读帧成功时刻（不含传感器/驱动缓冲；论文中可表述为“帧进入处理链路”）
            t_capture = time.time()

            annotated, dets = svc.infer(frame)
            alarms = svc.evaluate_alarms(dets, frame_shape_hw=(annotated.shape[0], annotated.shape[1]))

            # 若触发告警：保存带框图片 + 写入数据库
            for a in alarms:
                rel_path = save_event_image(settings.events_dir, annotated)
                meta = {"alarms": alarms, "detections": dets}
                ev = Event(alarm_type=a["alarm_type"], image_path=rel_path, meta_json=json.dumps(meta, ensure_ascii=False))
                db.add(ev)
                db.commit()
                db.refresh(ev)

            # 限制发送帧率
            now = time.time()
            if now - last_send < 1.0 / fps_limit:
                await asyncio.sleep(0.001)
                continue
            last_send = now

            jpeg_b64 = bgr_to_jpeg_base64(annotated, quality=80)
            await ws.send_text(
                json.dumps(
                    {
                        "type": "frame",
                        "jpeg": jpeg_b64,
                        "detections": dets,
                        "alarms": alarms,
                        "t_capture": t_capture,
                        "ts": now,
                    },
                    ensure_ascii=False,
                )
            )
    except WebSocketDisconnect:
        pass
    finally:
        try:
            cap.release()
        except Exception:
            pass
        try:
            db.close()
        except Exception:
            pass

