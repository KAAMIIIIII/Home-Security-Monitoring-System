# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

毕业设计：**基于YOLO的家庭安防监控系统的设计与实现**。

- 前端：Vue 3 + TypeScript + Element Plus + Vue Router + Pinia, 在 `frontend/` 目录
- 后端：FastAPI + WebSocket + YOLOv11 推理 + SQLite, 在 `backend/` 目录
- 模型：`models/best.pt`（8类检测：Cat/Person/Dog/Knife/Fire/Smoke/Door/Window/Crowbar）
- Python 版本：启动说明推荐 3.10/3.11，当前 `.venv` 为 3.9，均可正常运行
- 无自动化测试（前端/后端均无）
- 无 `.env` 文件，所有配置由 `backend/app/config.py` 中的代码默认值提供
- 完整启动说明见根目录 `毕业设计启动说明.md`

注意：根目录 `package.json` 和 `node_modules/` 是旧的模板项目残留，实际工作目录是 `frontend/` 和 `backend/`。`.gitignore` 也是前端模板遗留，未覆盖 Python 产物（`__pycache__/`、`.venv/`、`*.pyc`、`backend/data/`），这些目录/文件可能出现在 `git status` 中。

## 启动命令

**后端：**

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate         # Windows
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**前端：**

```bash
cd frontend
npm install
npm run dev          # 开发模式（vite --host，局域网可访问）
npm run build        # 生产构建 → frontend/dist/
npm run preview      # 预览生产构建（vite preview --host）
npx vue-tsc --noEmit # TypeScript 类型检查
```

后端运行在 `127.0.0.1:8000`，前端 Vite dev server 通过 proxy 将 `/api` 和 `/static` 请求转发到后端。生产部署时将 `frontend/dist/` 作为静态文件由后端或 Nginx 提供服务。

## 架构

### 后端 (`backend/`)

```
main.py                     # FastAPI 应用入口，挂载路由、CORS、静态文件
app/
  config.py                 # pydantic-settings 配置（阈值、路径、摄像头源等，运行时可改）
  db.py                     # SQLAlchemy engine + session + 目录初始化
  models.py                 # Event 表（id, created_at, alarm_type, image_path, meta_json）
  schemas.py                # Pydantic schema（SettingsIn/Out, RoiIn, BatchDeleteIn, EventOut）
  yolo_service.py           # YOLO 推理 + 业务告警逻辑（核心文件）
  tracker.py                # 简单 IoU 匹配追踪器（用于武器移动检测、人员入侵追踪）
  routes/
    settings.py             # GET/POST /api/settings — 运行时读写检测参数
    roi.py                  # POST /api/upload/roi — 上传禁区多边形
    events.py               # GET/DELETE /api/events — 告警事件查询/删除 + 过期清理
    stream.py               # WebSocket /api/video/stream — 实时视频推流
  utils/
    geometry.py             # 射线法、线段相交、bbox IoU/中心点、bbox与多边形相交判定
    image.py                # JPEG 编码 Base64、事件图片保存
```

- 配置在 `backend/app/config.py` 中通过 `pydantic-settings` 定义，运行时修改 `settings.xxx` 即可生效。**注意：配置仅存储在内存中，重启后端后恢复代码默认值，不会持久化。**
- `video_source` 支持摄像头索引字符串（`"0"`, `"1"`）或 RTSP/HTTP URL（如 `"rtsp://..."`）
- 关键默认值：`conf_thres=0.35`, `iou_thres=0.45`, `fire_smoke_conf_thres=0.58`, `fire_smoke_consecutive_frames=3`, `fire_smoke_region_iou_min=0.22`, `weapon_move_px_thres=18.0`, `alarm_cooldown_sec=5.0`, `retention_days=7`。入侵时序参数：`door_iou_thres=0.3`, `door_intrusion_min_dwell_frames=3`, `door_intrusion_disappear_missing_frames=6`, `person_track_match_iou=0.2`, `person_track_max_missing=14`。完整列表见 `config.py`。
- 数据库 `backend/data/app.db`（SQLite）在首次启动时由 `Base.metadata.create_all` 自动创建，无需手动迁移
- 模型加载延迟初始化 `YoloSecurityService`（在第一个 WebSocket 连接时才加载模型）
- 告警业务规则：火灾/烟雾需要连续N帧+高置信度；刀具需要中心点位移超过阈值；门窗/禁区入侵需要时序停留+离开/丢检
- `SimpleCentroidTracker` 有两套实例：`weapon_tracker`（刀具/撬棍移动）和 `person_intrusion_tracker`（人员闯入追踪），参数不同
- 告警冷却：同类型告警最小间隔由 `alarm_cooldown_sec` 控制（默认 5 秒）
- **模型路径解析**：优先查找 `../models/best.pt`（相对于 `backend/` 启动目录），失败时回退到 `yolo_service.py` 所在目录的 `../../models/best.pt`
- **YOLO 类别索引（CLASS_NAMES）**：`0=Cat, 1=Person, 2=Dog, 3=Knife, 4=Fire, 5=Smoke, 6=Door/Window, 7=Crowbar` — 顺序不可随意更改
- **告警类型**：`Fire`(HIGH)、`Smoke`(HIGH)、`WeaponMove`(MEDIUM)、`Intrusion`(HIGH)，冷却键分别为 `Fire`, `Smoke`, `WeaponMove_Knife`, `WeaponMove_Crowbar`, `Intrusion_Door`, `Intrusion_ROI`

### API 端点一览

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/health` | 健康检查 |
| `GET` | `/api/settings` | 读取当前运行配置 |
| `POST` | `/api/settings` | 修改检测参数（`conf_thres`, `iou_thres`, `retention_days`） |
| `POST` | `/api/upload/roi` | 上传禁区多边形（归一化坐标 `[[x,y],...]`） |
| `GET` | `/api/events` | 获取告警事件列表（按时间倒序，附带清理过期记录） |
| `DELETE` | `/api/events/batch` | 批量删除事件（`{ids: [...]}`） |
| `DELETE` | `/api/events/{id}` | 删除单条事件 |
| `WS` | `/api/video/stream` | 实时视频推流（WebSocket） |

- 前端通过 Vite proxy（`/api` `/static` → `http://127.0.0.1:8000`）访问后端，开发和生产环境 API 路径保持一致
- 事件列表接口自带过期清理：每次 GET /api/events 自动删除超过 `retention_days` 的旧记录和图片文件

### 前端 (`frontend/`)

```
src/
  main.ts                   # 入口：挂载 Vue + Pinia + Element Plus + Router
  App.vue                   # 根组件，渲染 MainLayout
  layout/MainLayout.vue     # 侧边栏导航布局
  router/index.ts           # 4 个路由：/ → /dashboard, /monitor, /events, /settings
  stores/
    monitor.ts              # WebSocket 连接管理、视频帧接收、FPS/延迟统计、告警 sticky 列表（Composition API）
    events.ts               # 告警事件列表 CRUD（Options API）
    settings.ts             # 运行时设置读写（Options API）
  views/
    Dashboard.vue           # 首页概览：今日/累计告警数统计
    Monitor.vue             # 实时监控：组合 VideoStream + StatsOverlay + AlarmPanel
    Events.vue              # 事件记录：组合 EventsTable + ImagePreview
    Settings.vue            # 系统设置：置信度/IoU 滑块、保留天数、RoiCanvas 禁区绘制
  components/
    common/PageHeader.vue   # 页面标题栏（title + #extra 插槽）
    monitor/VideoStream.vue # <img> 渲染 JPEG base64 帧 + @load 计算端到端延迟
    monitor/StatsOverlay.vue # 叠加显示 FPS + 延迟
    monitor/AlarmPanel.vue  # 实时告警卡片列表
    events/EventsTable.vue  # 事件表格（批量删除 + 点击查看大图）
    events/ImagePreview.vue # 大图预览对话框
    settings/RoiCanvas.vue  # Canvas 禁区多边形编辑器（归一化坐标 [0,1]）
  api/http.ts               # Axios 实例（baseURL 为空，依赖 Vite proxy）
  utils/
    date.ts                 # 时间格式化（UTC → 北京时间显示）
    alarm.ts                # alarmTypeZh：Fire→火灾, Smoke→烟雾, Intrusion→闯入, WeaponMove→刀具/撬棍危险移动
  styles/theme.css          # 暗色主题 CSS 变量（--bg/--panel/--border/--text/--muted/--brand/--danger）+ Element Plus 组件覆盖
```

- 组件已从 views 中抽取到 `frontend/src/components/`，按功能分目录：`common/`（通用）、`monitor/`（监控页）、`events/`（事件页）、`settings/`（设置页）
- `npm run dev` 执行 `vite --host`（绑定 `0.0.0.0`，局域网可访问），Vite proxy 将 `/api` 和 `/static` 转发到 `http://127.0.0.1:8000`
- tsconfig 无路径别名，所有 import 使用相对路径（如 `../../stores/monitor`）
- Monitor 页面通过 WebSocket 接收 JPEG base64 帧，`<img>` 标签 onload 事件计算端到端延迟（EMA 平滑，系数 0.22）
- 告警在 Monitor 侧栏 sticky 显示（默认保留 10 分钟，最多 5 条可见，实际缓存 20 条）
- WebSocket 协议：前端发送 `{type: 'start'}`，后端推送 `{type: 'frame', jpeg, t_capture, detections, alarms, ts}` 或 `{type: 'error', message}`
- **WebSocket URL 是硬编码的** (`ws://127.0.0.1:8000/api/video/stream`)，绕过 Vite proxy 直连后端端口。部署到非本地环境时需要修改
- **WebSocket 无自动重连**：连接断开后 `running` 置为 `false`，用户需手动点击 UI 重新连接
- 后端推流帧率限制为 15 FPS，JPEG 编码质量 80，避免前端卡顿
- `YoloSecurityService` 通过模块级 `get_service()` 实现延迟单例：首个 WebSocket 连接时才加载模型
