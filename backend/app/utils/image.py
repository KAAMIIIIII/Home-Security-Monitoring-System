import base64
import os
from datetime import datetime
import cv2


def bgr_to_jpeg_base64(frame_bgr, quality: int = 80) -> str:
    ok, buf = cv2.imencode(".jpg", frame_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)])
    if not ok:
        return ""
    return base64.b64encode(buf.tobytes()).decode("utf-8")


def save_event_image(events_dir: str, frame_bgr) -> str:
    """
    保存告警抓拍（带框标注的那一帧）
    返回相对路径：events/xxx.jpg（给前端拼接成 /static/...）
    """
    os.makedirs(events_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"event_{ts}.jpg"
    abs_path = os.path.join(events_dir, filename)
    cv2.imwrite(abs_path, frame_bgr)
    return f"events/{filename}"

