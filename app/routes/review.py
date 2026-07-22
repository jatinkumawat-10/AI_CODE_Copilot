from fastapi import APIRouter
from app.schemas.request import ReviewRequest
from app.schemas.response import ReviewResponse
from app.services.review_service import review_code 

router = APIRouter()
@router.post("/review", response_model=ReviewResponse)
def review(request: ReviewRequest):
    review = review_code(
        code=request.code,
        language=request.language
    )
    return ReviewResponse(review=review )

