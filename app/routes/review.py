from fastapi import APIRouter
from app.schemas.request import ReviewRequest
from app.schemas.response import ReviewResponse
from app.services.review_service import review_code 
from fastapi import UploadFile, File, Form

from app.utils.file_handler import read_uploaded_code

router = APIRouter()
@router.post("/review", response_model=ReviewResponse)
def review(request: ReviewRequest):
    review = review_code(
        code=request.code,
        language=request.language
    )
    return ReviewResponse(review=review )

@router.post("/review/file", response_model=ReviewResponse)
async def review_file(
    file: UploadFile = File(...),
    language: str = Form(...)
):
    """
    Review source code uploaded as a file.
    """

    code = await read_uploaded_code(file)

    result = review_code(
        code=code,
        language=language
    )

    return ReviewResponse(
        review=result
    )