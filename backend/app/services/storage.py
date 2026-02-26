"""
Storage service - swap via STORAGE_BACKEND env var.
Supports: local | s3
"""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile

from app.core.config import settings


async def save_file(upload: UploadFile, subfolder: str = "books") -> str:
    """Save uploaded file and return its path/key."""
    ext = Path(upload.filename).suffix if upload.filename else ""
    filename = f"{uuid.uuid4()}{ext}"

    if settings.STORAGE_BACKEND == "s3":
        return await _save_s3(upload, f"{subfolder}/{filename}")
    else:
        return await _save_local(upload, subfolder, filename)


async def _save_local(upload: UploadFile, subfolder: str, filename: str) -> str:
    base = Path(settings.LOCAL_STORAGE_PATH) / subfolder
    base.mkdir(parents=True, exist_ok=True)
    dest = base / filename
    content = await upload.read()
    dest.write_bytes(content)
    return f"{subfolder}/{filename}"


async def _save_s3(upload: UploadFile, key: str) -> str:
    import boto3

    s3 = boto3.client("s3", region_name=settings.AWS_REGION)
    content = await upload.read()
    s3.put_object(
        Bucket=settings.AWS_BUCKET,
        Key=key,
        Body=content,
        ContentType=upload.content_type or "application/octet-stream",
    )
    return key


def get_file_url(path: str) -> str:
    """Return accessible URL for a stored file."""
    if settings.STORAGE_BACKEND == "s3":
        return f"https://{settings.AWS_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{path}"
    return f"/files/{path}"
