from fastapi import FastAPI

from app.exceptions import LLMServiceError
from app.handlers.exception_handlers import llm_service_exception_handler
from app.middleware.request_id import request_id_middleware
from app.routes import health
from app.routes.review import router as review_router

app = FastAPI()

app.middleware("http")(request_id_middleware)

app.add_exception_handler(
    LLMServiceError,
    llm_service_exception_handler,
)


@app.get("/")
def home():
    return {"message": "Welcome to Code Review Copilot"}


app.include_router(
    review_router,
    prefix="/api/v1",
    tags=["Review"],
)

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"],
)
