import logging

from fastapi import Request
from fastapi.responses import JSONResponse


logger = logging.getLogger(
    "enterprise_ai_assistant"
)


async def global_exception_handler(
    request: Request,
    exc: Exception,
):

    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    logger.exception(
        "Unhandled application exception. "
        "path=%s request_id=%s",
        request.url.path,
        request_id,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": (
                "An internal server error "
                "occurred."
            ),
            "request_id": request_id,
        },
    )