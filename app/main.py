from fastapi import FastAPI
from app.routes.review import router as review_router
app = FastAPI()

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