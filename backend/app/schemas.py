from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class SettingsOut(BaseModel):
    conf_thres: float
    iou_thres: float
    retention_days: int
    roi_polygon: list = Field(default_factory=list)


class SettingsIn(BaseModel):
    conf_thres: Optional[float] = None
    iou_thres: Optional[float] = None
    retention_days: Optional[int] = None


class RoiIn(BaseModel):
    # 归一化坐标点：[[x,y],...], x/y ∈ [0,1]
    points: List[List[float]]


class BatchDeleteIn(BaseModel):
    ids: List[int]


class EventOut(BaseModel):
    id: int
    created_at: datetime
    alarm_type: str
    image_url: str
    meta: Any = {}

