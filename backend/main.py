import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db import Base, engine, ensure_data_dirs
from app.routes.settings import router as settings_router
from app.routes.roi import router as roi_router
from app.routes.events import router as events_router
from app.routes.stream import router as stream_router
from app.config import settings


def create_app():
    ensure_data_dirs()
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="家庭安防监控系统", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 事件图片静态服务：/static/events/xxx.jpg
    app.mount("/static", StaticFiles(directory=settings.data_dir), name="static")

    app.include_router(settings_router)
    app.include_router(roi_router)
    app.include_router(events_router)
    app.include_router(stream_router)

    @app.get("/api/health")
    def health():
        return {"ok": True}

    return app


app = create_app()

