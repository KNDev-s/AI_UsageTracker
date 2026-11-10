from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.modules.accounts.router import router as accounts_router
from app.modules.auth.router import router as auth_router
from app.shared.exceptions import AppException
from app.shared.schemas import APIResponse, ErrorDetail, ErrorResponse


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/api/docs" if settings.app_env != "production" else None,
        redoc_url="/api/redoc" if settings.app_env != "production" else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-CSRF-Token", "X-Account-ID"],
    )

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
        body = ErrorResponse(
            error=ErrorDetail(code=exc.code, message=exc.message, details=exc.details)
        )
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        body = ErrorResponse(
            error=ErrorDetail(
                code="validation_error",
                message="Os dados enviados são inválidos.",
                details=exc.errors(),
            )
        )
        return JSONResponse(status_code=422, content=body.model_dump())

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
        body = ErrorResponse(
            error=ErrorDetail(code="http_error", message=str(exc.detail))
        )
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.get("/health", tags=["health"])
    def root_health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/health", response_model=APIResponse[dict[str, str]], tags=["health"])
    def api_health() -> APIResponse[dict[str, str]]:
        return APIResponse(data={"status": "ok", "env": settings.app_env})

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(accounts_router, prefix="/api/v1")
    return app


app = create_app()

