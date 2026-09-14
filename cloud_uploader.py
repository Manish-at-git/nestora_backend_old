import os
import json
import uuid
import mimetypes
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent
LOCAL_UPLOAD_DIR = ROOT_DIR / "uploads"
LOCAL_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def upload_to_uploadthing_sdk(file_bytes: bytes, filename: str, content_type: str) -> str:
    """
    Uploads a file to UploadThing using the official UploadThing SDK.
    Returns the public CDN URL (https://<appId>.ufs.sh/f/<key>).
    """
    token = os.getenv("UPLOADTHING_TOKEN", "").strip().strip("'\"")
    if not token:
        raise ValueError("UPLOADTHING_TOKEN is not configured in .env")

    helper_script = ROOT_DIR / "uploadthing_helper.mjs"
    if not helper_script.exists():
        raise RuntimeError(f"Helper script not found at {helper_script}")

    if not content_type or content_type == "application/octet-stream":
        content_type, _ = mimetypes.guess_type(filename)
        content_type = content_type or "application/octet-stream"

    ext = Path(filename).suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        env = {**os.environ, "UPLOADTHING_TOKEN": token}
        proc = subprocess.run(
            ["node", str(helper_script), tmp_path, filename, content_type],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(ROOT_DIR),
            timeout=45
        )

        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        if not stdout:
            raise RuntimeError(f"UploadThing bridge produced no output. Code: {proc.returncode}, Stderr: {stderr}")

        try:
            result = json.loads(stdout)
        except json.JSONDecodeError:
            raise RuntimeError(f"Failed to parse uploader response: {stdout} | Stderr: {stderr}")

        if not result.get("ok") or not result.get("url"):
            error_msg = result.get("error", "Unknown error from UploadThing SDK")
            raise RuntimeError(f"UploadThing error: {error_msg}")

        return result["url"]

    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def save_locally_fallback(file_bytes: bytes, filename: str) -> str:
    """Fallback to save in local uploads directory if external cloud is unreachable."""
    ext = Path(filename).suffix or ".bin"
    unique_name = f"{uuid.uuid4()}{ext}"
    dest = LOCAL_UPLOAD_DIR / unique_name
    with open(dest, "wb") as f:
        f.write(file_bytes)
    return f"/uploads/{unique_name}"


# ==============================================================================
# 1. MEDIA ASSET UPLOAD (Images & Videos)
# ==============================================================================
async def upload_media_asset(file: UploadFile) -> Dict[str, Any]:
    """
    Uploads Images and Videos.
    * Currently uses UploadThing.
    * When switching to Cloudinary later, modify ONLY this function.
    """
    filename = file.filename or "media.png"
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        cdn_url = upload_to_uploadthing_sdk(
            file_bytes=contents,
            filename=filename,
            content_type=file.content_type or "image/jpeg"
        )
        logger.info(f"Cloud media upload successful: {cdn_url}")
        return {
            "ok": True,
            "url": cdn_url,
            "filename": filename,
            "asset_type": "media",
            "provider": "uploadthing"
        }
    except Exception as e:
        logger.error(f"Cloud media upload error: {e}. Saving local fallback.")
        local_url = save_locally_fallback(contents, filename)
        return {
            "ok": True,
            "url": local_url,
            "filename": filename,
            "asset_type": "media",
            "provider": "local_fallback"
        }


# ==============================================================================
# 2. DOCUMENT ASSET UPLOAD (PDF, Excel, Docs, etc.)
# ==============================================================================
async def upload_document_asset(file: UploadFile) -> Dict[str, Any]:
    """
    Uploads Documents and Files (PDF, Excel, Word, CSV, ZIP, etc.).
    * Uploaded to UploadThing.
    """
    filename = file.filename or "document.bin"
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        cdn_url = upload_to_uploadthing_sdk(
            file_bytes=contents,
            filename=filename,
            content_type=file.content_type or "application/octet-stream"
        )
        logger.info(f"Cloud document upload successful: {cdn_url}")
        return {
            "ok": True,
            "url": cdn_url,
            "filename": filename,
            "asset_type": "document",
            "provider": "uploadthing"
        }
    except Exception as e:
        logger.error(f"Cloud document upload error: {e}. Saving local fallback.")
        local_url = save_locally_fallback(contents, filename)
        return {
            "ok": True,
            "url": local_url,
            "filename": filename,
            "asset_type": "document",
            "provider": "local_fallback"
        }
