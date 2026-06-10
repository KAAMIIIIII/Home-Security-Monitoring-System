import json
import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Event
from ..config import settings
from ..schemas import EventOut, BatchDeleteIn


router = APIRouter(prefix="/api/events", tags=["events"])


def cleanup_expired(db: Session):
    """
    清理超过保留天数的事件记录与图片文件。
    说明：为了降低复杂度，这里采用“访问/写入时顺便清理”的方式，
    不需要额外引入定时任务组件，毕业设计演示足够。
    """
    days = int(settings.retention_days or 7)
    expire_before = datetime.now(timezone.utc) - timedelta(days=days)
    old = db.query(Event).filter(Event.created_at < expire_before).all()
    for e in old:
        # 删除图片文件
        abs_img = os.path.join(settings.data_dir, e.image_path.replace("events/", "events" + os.sep))
        try:
            if os.path.exists(abs_img):
                os.remove(abs_img)
        except Exception:
            pass
        db.delete(e)
    if old:
        db.commit()


@router.get("", response_model=list[EventOut])
def list_events(db: Session = Depends(get_db)):
    cleanup_expired(db)
    items = db.query(Event).order_by(Event.created_at.desc()).all()
    out = []
    for e in items:
        try:
            meta = json.loads(e.meta_json or "{}")
        except Exception:
            meta = {}
        out.append(
            EventOut(
                id=e.id,
                created_at=e.created_at,
                alarm_type=e.alarm_type,
                image_url=f"/static/{e.image_path}",
                meta=meta,
            )
        )
    return out


@router.delete("/batch")
def delete_events_batch(body: BatchDeleteIn, db: Session = Depends(get_db)):
    events = db.query(Event).filter(Event.id.in_(body.ids)).all()
    for e in events:
        abs_img = os.path.join(settings.data_dir, e.image_path.replace("events/", "events" + os.sep))
        try:
            if os.path.exists(abs_img):
                os.remove(abs_img)
        except Exception:
            pass
        db.delete(e)
    db.commit()
    return {"ok": True, "deleted": len(events)}


@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    e = db.query(Event).filter(Event.id == event_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="事件不存在")
    abs_img = os.path.join(settings.data_dir, e.image_path.replace("events/", "events" + os.sep))
    try:
        if os.path.exists(abs_img):
            os.remove(abs_img)
    except Exception:
        pass
    db.delete(e)
    db.commit()
    return {"ok": True}

