from fastapi import FastAPI
from app.routes.review import router as review_router
from fastapi.responses import JSONResponse
from app.exceptions import LLMServiceError
app = FastAPI()

@app.exception_handler(LLMServiceError)
async def llm_exception_handler(request, exc):

    return JSONResponse(
        status_code=503,
        content={
            "detail": str(exc)
        },
    )

@app.get("/")
def home():
    return {
        "message":"Welcome to Code Review Copilot"
        }
@app.get("/health")
def health():
    return{
        "status":"ok"
    }
# path parameters -> variables passed in the URL path
# @app.get("/review")
# def review(language: str = "python"):
#     return {
#         "language": language
#     }

app.include_router(review_router)