# 家庭安防监控系统

基于 **YOLOv11** 的家庭安防监控系统。

## 功能特性

- 🔍 **8 类实时检测**：人员、猫、狗、刀具、火灾、烟雾、门窗、撬棍
- 🔥 **火灾/烟雾告警**：连续帧+高置信度判定，降低误报
- 🔪 **武器危险移动检测**：基于 IoU 追踪 + 中心点位移阈值
- 🚪 **门窗/禁区入侵检测**：时序停留+离开判定，支持自定义 ROI 多边形
- 📹 **WebSocket 实时推流**：15 FPS 低延迟视频传输
- 📊 **告警事件管理**：历史记录查询、批量删除、自动过期清理
- ⚙️ **运行时可调参数**：置信度、IoU、告警冷却等无需重启

## 技术栈

| 层级 | 技术                                                          |
| ---- | ------------------------------------------------------------- |
| 前端 | Vue 3 + TypeScript + Element Plus + Pinia + Vue Router + Vite |
| 后端 | FastAPI + WebSocket + SQLAlchemy + SQLite                     |
| 模型 | YOLOv11 (Ultralytics) + OpenCV                                |
| 算法 | 射线法、IoU 匹配、质心追踪                                    |

## 项目结构

```
├── frontend/                # Vue 3 前端
│   └── src/
│       ├── views/           # Dashboard / Monitor / Events / Settings
│       ├── components/      # monitor / events / settings / common
│       ├── stores/          # Pinia 状态管理
│       ├── router/          # 路由配置
│       ├── api/             # Axios 封装
│       ├── utils/           # 工具函数（时间格式化、告警类型映射）
│       └── styles/          # 暗色主题
├── backend/                 # FastAPI 后端
│   ├── main.py              # 应用入口
│   └── app/
│       ├── config.py        # 运行时配置（pydantic-settings）
│       ├── yolo_service.py  # YOLO 推理 + 告警业务（核心）
│       ├── tracker.py       # 目标追踪器
│       ├── models.py        # 数据库模型
│       ├── schemas.py       # Pydantic 校验
│       ├── routes/          # API 路由（settings/roi/events/stream）
│       └── utils/           # 几何计算 / 图像工具
└── models/
    └── best.pt              # YOLOv11 训练权重
```

## 环境要求

- **OS**：Windows 10/11
- **Python**：3.10 / 3.11（3.9 亦可）
- **Node.js**：18+（推荐 20）
- **模型文件**：确保 `models/best.pt` 存在

## 快速启动

### 1. 启动后端

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate       # Windows
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

后端运行在 `http://127.0.0.1:8000`。

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev       # 开发模式（Vite --host，局域网可访问）
```

前端开发服务器默认绑定 `0.0.0.0`，Vite 会自动代理 `/api` 和 `/static` 到后端。

### 3. 访问系统

浏览器打开终端输出的地址（通常是 `http://localhost:5173`），即可进入监控面板。

## API 端点

| 方法     | 路径                | 说明             |
| -------- | ------------------- | ---------------- |
| `GET`    | `/api/health`       | 健康检查         |
| `GET`    | `/api/settings`     | 读取运行配置     |
| `POST`   | `/api/settings`     | 修改检测参数     |
| `POST`   | `/api/upload/roi`   | 上传禁区多边形   |
| `GET`    | `/api/events`       | 获取告警事件列表 |
| `DELETE` | `/api/events/batch` | 批量删除事件     |
| `DELETE` | `/api/events/{id}`  | 删除单条事件     |
| `WS`     | `/api/video/stream` | 实时视频推流     |

## 检测类别与告警类型

| 类别                        | 告警类型   | 等级      |
| --------------------------- | ---------- | --------- |
| Fire（火灾）                | Fire       | 🔴 HIGH   |
| Smoke（烟雾）               | Smoke      | 🔴 HIGH   |
| Knife / Crowbar（武器移动） | WeaponMove | 🟡 MEDIUM |
| Door / Window / ROI（闯入） | Intrusion  | 🔴 HIGH   |
| Cat / Dog / Person          | —          | 无告警    |

## 配置参数

运行中可通过设置页面实时调整，关键参数默认值：

- 置信度阈值：`0.35`
- IoU 阈值：`0.45`
- 火烟连续帧：`3`
- 告警冷却：`5` 秒
- 记录保留：`7` 天

完整列表见 `backend/app/config.py`。

## 生产部署

```bash
# 前端构建
cd frontend && npm run build    # 产出 dist/

# 后端直接服务静态文件，或使用 Nginx 反向代理
```

## License

MIT
