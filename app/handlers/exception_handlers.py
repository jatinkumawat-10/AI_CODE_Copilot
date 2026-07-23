from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import LLMServiceError
from app.schemas.error import ErrorResponse

async def llm_service_exception_handler(
    request: Request,
    exc: LLMServiceError,
):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            code="LLM_ERROR",
            message=str(exc),
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(),
    )  