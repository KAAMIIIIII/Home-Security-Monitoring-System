from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    系统运行配置
    """

    # 模型路径
    model_path: str = "../models/best.pt"
    #摄像头源
    video_source: str = "0"

    # 检测参数阈值
    conf_thres: float = 0.35
    iou_thres: float = 0.45

    # 告警图片保留天数
    retention_days: int = 7

    # 门窗入侵：Person 与 Door/Window 框 IoU 或中心点在门窗口内，用于定义「人在敏感区内」
    door_iou_thres: float = 0.3
    # 时序闯入（门窗 + ROI 禁区共用）：连续多少帧在敏感区内才视为一次有效「进入」
    door_intrusion_min_dwell_frames: int = 3
    # 已进入敏感区后，连续多少帧未检测到该人（track missing）则视为「消失」并告警
    door_intrusion_disappear_missing_frames: int = 6
    # 人员跟踪（门窗 / ROI 时序闯入）：与上一帧框 IoU 匹配、最大丢检帧数（须大于上一项）
    person_track_match_iou: float = 0.2
    person_track_max_missing: int = 14

    # 刀具/撬棍危险移动判定阈值（像素/帧）
    weapon_move_px_thres: float = 18.0

    # 同类型告警最小间隔（秒），防止刷屏
    alarm_cooldown_sec: float = 5.0

    # 火灾/烟雾：单独提高置信度门槛，且需同一区域连续多帧才告警（减少误报）
    fire_smoke_conf_thres: float = 0.58
    fire_smoke_consecutive_frames: int = 3
    # 与上一帧候选框 IoU ≥ 此值视为同一区域（框抖动或烟雾形变时可略调低）
    fire_smoke_region_iou_min: float = 0.22

    # 禁区多边形点
    roi_polygon: list = []

    # 数据目录
    data_dir: str = "./data"
    events_dir: str = "./data/events"
    db_url: str = "sqlite:///./data/app.db"


settings = Settings()

