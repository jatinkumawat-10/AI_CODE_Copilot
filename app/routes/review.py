from fastapi import APIRouter, UploadFile, File

from app.schemas.review import ReviewResult
from app.schemas.request import ReviewRequest
from app.services.review_service import review_code
from app.utils.file_handler import (
    read_uploaded_code,
    detect_language,
)

router = APIRouter()


@router.post("/review", response_model=ReviewResult)
def review(request: ReviewRequest):
    """
    Review source code submitted as JSON.
    """
    result = review_code(
        code=request.code,
        language=request.language,
    )

    return result


@router.post("/review/file", response_model=ReviewResult)
async def review_file(
    file: UploadFile = File(...),
):
    """
    Review source code uploaded as a file.
    """
    code = await read_uploaded_code(file)

    language = detect_language(file.filename)

    result = review_code(
        code=code,
        language=language,
    )

    return result