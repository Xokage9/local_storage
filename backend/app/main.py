from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.storages import router as storages_router
from app.api.v1.folders import router as folders_router
from app.api.v1.files import router as files_router
from app.api.v1.share_links import router as share_links_router
from app.api.v1.admin import router as admin_router


def create_app() -> FastAPI:
    app = FastAPI(title="Storage Service", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(storages_router, prefix="/api/v1")
    app.include_router(folders_router, prefix="/api/v1")
    app.include_router(files_router, prefix="/api/v1")
    app.include_router(share_links_router, prefix="/api/v1")
    app.include_router(admin_router, prefix="/api/v1")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
