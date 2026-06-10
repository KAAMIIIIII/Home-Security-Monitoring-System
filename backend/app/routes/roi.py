from fastapi import APIRouter
from ..config import settings
from ..schemas import RoiIn, SettingsOut


router = APIRouter(prefix="/api/upload/roi", tags=["roi"])


@router.post("", response_model=SettingsOut)
def upload_roi(body: RoiIn):
    # 简单校验：至少 3 个点
    pts = body.points or []
    if len(pts) < 3:
        settings.roi_polygon = []
    else:
        # 归一化点，裁剪到 [0,1]
        norm = []
        for x, y in pts:
            x = max(0.0, min(1.0, float(x)))
            y = max(0.0, min(1.0, float(y)))
            norm.append([x, y])
        settings.roi_polygon = norm
    return SettingsOut(
        conf_thres=settings.conf_thres,
        iou_thres=settings.iou_thres,
        retention_days=settings.retention_days,
        roi_polygon=settings.roi_polygon or [],
    )

