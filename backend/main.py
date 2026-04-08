from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import adversarial, analyze, fingerprint, report, result


def create_app() -> FastAPI:
    app = FastAPI(title="Spectre API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(analyze.router, prefix="/api", tags=["analyze"])
    app.include_router(result.router, prefix="/api", tags=["result"])
    app.include_router(report.router, prefix="/api", tags=["report"])
    app.include_router(fingerprint.router, prefix="/api", tags=["fingerprint"])
    app.include_router(adversarial.router, prefix="/api", tags=["adversarial"])

    return app


app = create_app()