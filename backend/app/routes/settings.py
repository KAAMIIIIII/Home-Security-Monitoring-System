from fastapi import APIRouter
from ..config import settings
from ..schemas import SettingsOut, SettingsIn


router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsOut)
def get_settings():
    return SettingsOut(
        conf_thres=settings.conf_thres,
        iou_thres=settings.iou_thres,
        retention_days=settings.retention_days,
        roi_polygon=settings.roi_polygon or [],
    )


@router.post("", response_model=SettingsOut)
def update_settings(body: SettingsIn):
    if body.conf_thres is not None:
        settings.conf_thres = float(body.conf_thres)
    if body.iou_thres is not None:
        settings.iou_thres = float(body.iou_thres)
    if body.retention_days is not None:
        settings.retention_days = int(body.retention_days)
    return get_settings()

