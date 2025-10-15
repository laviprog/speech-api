import os
import re
import tempfile
from pathlib import Path

from fastapi import UploadFile

ALLOWED_EXT = {".wav", ".mp3"}

BASE_TMP_DIR = Path(os.getenv("TRANSCRIBE_TMP_DIR", "/tmp/transcribe"))
BASE_TMP_DIR.mkdir(parents=True, exist_ok=True)

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")
CHUNK = 1024 * 1024  # 1 MB


def _sanitize(name: str) -> str:
    name = name or "audio"
    name = _SAFE.sub("_", name)
    return name[:128]


async def save_upload_to_temp(file: UploadFile) -> str:
    orig = _sanitize(file.filename or "audio")
    ext = Path(orig).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise ValueError(
            f"Unsupported file type: {ext or 'no extension'} (allowed: {', '.join(ALLOWED_EXT)})"
        )

    with tempfile.NamedTemporaryFile(
        mode="wb", prefix="stt_", suffix=ext, dir=BASE_TMP_DIR, delete=False
    ) as tmp:
        tmp_path = Path(tmp.name)
        file.file.seek(0)
        while True:
            chunk = file.file.read(CHUNK)
            if not chunk:
                break
            tmp.write(chunk)
    return str(tmp_path.resolve())
