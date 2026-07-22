from pathlib import Path
from fastapi import UploadFile, HTTPException

ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".java",
    ".ts",
    ".cpp",
}


async def read_uploaded_code(file: UploadFile) -> str:
    """
    Validate and read uploaded source code.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}"
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    try:
        code = contents.decode("utf-8")

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded."
        )

    return code