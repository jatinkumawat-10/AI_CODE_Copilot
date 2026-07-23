from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.utils.file_handler import (
    detect_language,
    read_uploaded_code,
)


# -------------------------
# detect_language()
# -------------------------

def test_detect_language_python():
    assert detect_language("main.py") == "python"


def test_detect_language_javascript():
    assert detect_language("app.js") == "javascript"


def test_detect_language_java():
    assert detect_language("Main.java") == "java"


def test_detect_language_invalid_extension():
    with pytest.raises(HTTPException) as exc:
        detect_language("notes.txt")

    assert exc.value.status_code == 400
    assert "Unsupported programming language" in exc.value.detail


# -------------------------
# read_uploaded_code()
# -------------------------

@pytest.mark.anyio
async def test_read_uploaded_code_success():
    file = UploadFile(
        filename="main.py",
        file=BytesIO(b"print('Hello')")
    )

    code = await read_uploaded_code(file)

    assert code == "print('Hello')"


@pytest.mark.anyio
async def test_read_uploaded_code_empty_file():
    file = UploadFile(
        filename="main.py",
        file=BytesIO(b"")
    )

    with pytest.raises(HTTPException) as exc:
        await read_uploaded_code(file)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Uploaded file is empty."


@pytest.mark.anyio
async def test_read_uploaded_code_invalid_extension():
    file = UploadFile(
        filename="notes.txt",
        file=BytesIO(b"Hello")
    )

    with pytest.raises(HTTPException) as exc:
        await read_uploaded_code(file)

    assert exc.value.status_code == 400
    assert "Unsupported file type" in exc.value.detail


@pytest.mark.anyio
async def test_read_uploaded_code_invalid_encoding():
    file = UploadFile(
        filename="main.py",
        file=BytesIO(b"\xff\xfe\xfd")
    )

    with pytest.raises(HTTPException) as exc:
        await read_uploaded_code(file)

    assert exc.value.status_code == 400
    assert exc.value.detail == "File must be UTF-8 encoded."

@pytest.mark.anyio
async def test_read_uploaded_code_file_too_large():
    file = UploadFile(
        filename="main.py",
        file=BytesIO(b"a" * (1024 * 1024 + 1))
    )

    with pytest.raises(HTTPException) as exc:
        await read_uploaded_code(file)

    assert exc.value.status_code == 400
    assert "maximum size" in exc.value.detail