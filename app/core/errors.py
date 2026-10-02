from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


STATUS_CODES = {
    401: "authentication_failed",
    404: "not_found",
    409: "conflict",
    413: "payload_too_large",
    422: "validation_error",
    503: "service_unavailable",
}


def error_payload(code: str, message: str, details: list[dict[str, Any]] | None = None) -> dict:
    error: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return {"error": error}


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    headers = exc.headers or {}
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(STATUS_CODES.get(exc.status_code, "http_error"), message),
        headers=headers,
    )


async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {"location": list(error["loc"]), "message": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=error_payload("validation_error", "Request validation failed", details),
    )


def install_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
