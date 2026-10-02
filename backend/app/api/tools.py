from pathlib import Path
import shutil
import uuid
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from backend.app.services.office.word_to_pdf import convert_word_to_pdf
from backend.app.services.office.pdf_to_word import convert_pdf_to_word
from backend.app.services.pdf_tools import (
    merge_pdfs, split_pdf, compress_pdf, rotate_pdf
)
from backend.app.services.image_tools import (
    resize_image, compress_image, convert_image, image_to_pdf
)

router = APIRouter(prefix="/api/tools", tags=["DocuLab Tools"])

BASE_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
OUTPUT_DIR = BASE_DIR / "storage" / "outputs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(file: UploadFile, suffix: str | None = None) -> Path:
    job_id = uuid.uuid4().hex
    safe_name = Path(file.filename or "upload").name
    if suffix:
        safe_name = Path(safe_name).stem + suffix
    path = UPLOAD_DIR / f"{job_id}_{safe_name}"
    with path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return path


def output_name(job_id: str, stem: str, ext: str) -> Path:
    return OUTPUT_DIR / f"{job_id}_{stem}{ext}"


@router.post("/word-to-pdf")
async def word_to_pdf(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".docx"):
        raise HTTPException(400, "Only .docx files are supported.")
    job = uuid.uuid4().hex
    src = save_upload(file)
    try:
        generated = convert_word_to_pdf(src, OUTPUT_DIR)
        target = output_name(job, Path(file.filename).stem, ".pdf")
        generated.rename(target)
        return FileResponse(target, media_type="application/pdf",
                            filename=f"{Path(file.filename).stem}.pdf")
    except Exception as exc:
        raise HTTPException(500, f"Word to PDF conversion failed: {exc}") from exc
    finally:
        src.unlink(missing_ok=True)


@router.post("/pdf-to-word")
async def pdf_to_word(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only .pdf files are supported.")
    job = uuid.uuid4().hex
    src = save_upload(file)
    try:
        generated = convert_pdf_to_word(src, OUTPUT_DIR)
        target = output_name(job, Path(file.filename).stem, ".docx")
        generated.rename(target)
        return FileResponse(
            target,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"{Path(file.filename).stem}.docx",
        )
    except Exception as exc:
        raise HTTPException(500, f"PDF to Word conversion failed: {exc}") from exc
    finally:
        src.unlink(missing_ok=True)


@router.post("/pdf-merge")
async def pdf_merge(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(400, "Upload at least two PDF files.")
    job = uuid.uuid4().hex
    paths = [save_upload(f) for f in files]
    target = output_name(job, "merged", ".pdf")
    try:
        merge_pdfs(paths, target)
        return FileResponse(target, media_type="application/pdf", filename="merged.pdf")
    except Exception as exc:
        raise HTTPException(500, f"PDF merge failed: {exc}") from exc
    finally:
        for p in paths: p.unlink(missing_ok=True)


@router.post("/pdf-split")
async def pdf_split(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only .pdf files are supported.")
    src = save_upload(file)
    try:
        outputs = split_pdf(src, OUTPUT_DIR, uuid.uuid4().hex)
        # Return the first page for the initial API milestone; full ZIP packaging can be added next.
        return FileResponse(outputs[0], media_type="application/pdf",
                            filename=Path(outputs[0]).name)
    except Exception as exc:
        raise HTTPException(500, f"PDF split failed: {exc}") from exc
    finally:
        src.unlink(missing_ok=True)


@router.post("/pdf-compress")
async def pdf_compress(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only .pdf files are supported.")
    src = save_upload(file)
    target = output_name(uuid.uuid4().hex, Path(file.filename).stem, ".pdf")
    try:
        compress_pdf(src, target)
        return FileResponse(target, media_type="application/pdf",
                            filename=f"{Path(file.filename).stem}_compressed.pdf")
    except Exception as exc:
        raise HTTPException(500, f"PDF compression failed: {exc}") from exc
    finally:
        src.unlink(missing_ok=True)


@router.post("/pdf-rotate")
async def pdf_rotate(file: UploadFile = File(...), degrees: int = 90):
    if degrees not in (90, 180, 270):
        raise HTTPException(400, "degrees must be 90, 180, or 270.")
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only .pdf files are supported.")
    src = save_upload(file)
    target = output_name(uuid.uuid4().hex, Path(file.filename).stem, ".pdf")
    try:
        rotate_pdf(src, target, degrees)
        return FileResponse(target, media_type="application/pdf",
                            filename=f"{Path(file.filename).stem}_rotated.pdf")
    except Exception as exc:
        raise HTTPException(500, f"PDF rotation failed: {exc}") from exc
    finally:
        src.unlink(missing_ok=True)


@router.post("/image-resize")
async def image_resize(file: UploadFile = File(...), width: int = 1000, height: int = 1000):
    if width < 1 or height < 1:
        raise HTTPException(400, "Width and height must be positive.")
    src = save_upload(file)
    target = output_name(uuid.uuid4().hex, Path(file.filename or "image").stem, ".jpg")
    try:
        resize_image(src, target, width, height)
        return FileResponse(target, media_type="image/jpeg", filename="resized.jpg")
    except Exception as exc:
        raise HTTPException(500, f"Image resize failed: {exc}") from exc
    finally:
        src.unlink(missing_ok=True)


@router.post("/image-compress")
async def image_compress(file: UploadFile = File(...), quality: int = 75):
    if not 1 <= quality <= 100:
        raise HTTPException(400, "quality must be between 1 and 100.")
    src = save_upload(file)
    target = output_name(uuid.uuid4().hex, Path(file.filename or "image").stem, ".jpg")
    try:
        compress_image(src, target, quality)
        return FileResponse(target, media_type="image/jpeg", filename="compressed.jpg")
    except Exception as exc:
        raise HTTPException(500, f"Image compression failed: {exc}") from exc
    finally:
        src.unlink(missing_ok=True)


@router.post("/image-convert")
async def image_convert(file: UploadFile = File(...), format: str = "png"):
    if format.lower() not in ("jpg", "jpeg", "png", "webp"):
        raise HTTPException(400, "format must be jpg, jpeg, png, or webp.")
    src = save_upload(file)
    ext = ".jpg" if format.lower() in ("jpg", "jpeg") else "." + format.lower()
    target = output_name(uuid.uuid4().hex, Path(file.filename or "image").stem, ext)
    try:
        convert_image(src, target, format)
        media = "image/jpeg" if ext == ".jpg" else f"image/{format.lower()}"
        return FileResponse(target, media_type=media, filename=target.name)
    except Exception as exc:
        raise HTTPException(500, f"Image conversion failed: {exc}") from exc
    finally:
        src.unlink(missing_ok=True)


@router.post("/image-to-pdf")
async def image_to_pdf_endpoint(file: UploadFile = File(...)):
    src = save_upload(file)
    target = output_name(uuid.uuid4().hex, Path(file.filename or "image").stem, ".pdf")
    try:
        image_to_pdf(src, target)
        return FileResponse(target, media_type="application/pdf", filename="image.pdf")
    except Exception as exc:
        raise HTTPException(500, f"Image to PDF failed: {exc}") from exc
    finally:
        src.unlink(missing_ok=True)
