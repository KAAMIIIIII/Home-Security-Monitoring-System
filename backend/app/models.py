from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone

from .db import Base


class Event(Base):
    """
    告警事件表
    - image_path: 保存“带框标注”的抓拍图片相对路径（用于前端展示）
    - meta_json: 附加信息（如检测到的目标、阈值等）JSON 字符串
    """

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    # 统一以 UTC 存储时间，避免“时区不一致导致前端显示偏移”。
    # 注意：数据库字段不强制 timezone=True 是为了 SQLite 简化；前端会按时区字符串/兼容逻辑显示北京时间。
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    alarm_type = Column(String(64), index=True)  # Fire/Smoke/Intrusion/WeaponMove
    image_path = Column(String(512), nullable=False)
    meta_json = Column(Text, default="{}")

