from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import adversarial, analyze, fingerprint, report, result
from core.bootstrap import ensure_runtime_dirs
from core.config import settings
from core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def on_startup() -> None:
        ensure_runtime_dirs()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(analyze.router, prefix=settings.api_prefix, tags=["analyze"])
    app.include_router(result.router, prefix=settings.api_prefix, tags=["result"])
    app.include_router(report.router, prefix=settings.api_prefix, tags=["report"])
    app.include_router(fingerprint.router, prefix=settings.api_prefix, tags=["fingerprint"])
    app.include_router(adversarial.router, prefix=settings.api_prefix, tags=["adversarial"])

    return app


app = create_app()