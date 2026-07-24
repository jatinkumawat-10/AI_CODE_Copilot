from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.request import ReviewRequest
from app.schemas.review import ReviewResult
from app.services.persistence_service import save_review_run
from app.services.review_service import generate_review
from app.utils.file_handler import (
    detect_language,
    read_uploaded_code,
)

router = APIRouter()


@router.post("/review", response_model=ReviewResult)
def review(request: ReviewRequest, db: Session = Depends(get_db)):
    """
    Review source code submitted as JSON, persisting the run to the database.
    """
    llm_response = generate_review(
        code=request.code,
        language=request.language,
    )

    save_review_run(
        db=db,
        code=request.code,
        language=request.language,
        llm_response=llm_response,
    )

    return llm_response.content


@router.post("/review/file", response_model=ReviewResult)
async def review_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Review source code uploaded as a file, persisting the run to the database.
    """
    code = await read_uploaded_code(file)

    language = detect_language(file.filename)

    llm_response = generate_review(
        code=code,
        language=language,
    )

    save_review_run(
        db=db,
        code=code,
        language=language,
        llm_response=llm_response,
        filename=file.filename,
    )

    return llm_response.content