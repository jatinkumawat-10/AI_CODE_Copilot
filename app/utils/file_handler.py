from pathlib import Path
from fastapi import UploadFile, HTTPException

from app.config import MAX_FILE_SIZE

EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".cpp": "cpp",
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

    if extension not in  EXTENSION_LANGUAGE_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}"
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
        status_code=400,
        detail="Uploaded file exceeds the maximum size limit."
    )

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

def detect_language(filename: str) -> str:
    """
    Detect programming language from a file extension.
    """

    extension = Path(filename).suffix.lower()

    try:
        return EXTENSION_LANGUAGE_MAP[extension]

    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported programming language: {extension}"
        )