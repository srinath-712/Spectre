from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import numpy as np
from fastapi import UploadFile

from core.config import settings


@dataclass(frozen=True)
class IngestedDocument:
    pages: list[np.ndarray]
    page_count: int
    ingested_pages: int
    source_type: str


async def read_upload_bytes(file: UploadFile) -> bytes:
    data = await file.read()
    if len(data) > settings.max_upload_bytes:
        raise ValueError(
            f"Uploaded file exceeds {settings.max_upload_mb}MB limit."
        )
    return data


def _decode_image_bytes(payload: bytes) -> np.ndarray:
    from PIL import Image

    image = Image.open(BytesIO(payload)).convert("RGB")
    array = np.array(image)

    # Convert RGB -> BGR when OpenCV is available so downstream CV ops are consistent.
    try:
        import cv2

        return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
    except Exception:
        return array


def _ingest_pdf(payload: bytes) -> IngestedDocument:
    try:
        import fitz  # PyMuPDF
    except Exception as exc:
        raise RuntimeError(
            "PyMuPDF is required for PDF ingestion. Install package 'pymupdf'."
        ) from exc

    pages: list[np.ndarray] = []
    with fitz.open(stream=payload, filetype="pdf") as document:
        page_count = document.page_count
        ingest_limit = min(page_count, settings.max_pdf_pages)

        for idx in range(ingest_limit):
            page = document.load_page(idx)
            pix = page.get_pixmap(dpi=settings.pdf_render_dpi, alpha=False)
            np_image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, pix.n
            )

            # PyMuPDF pixmap is RGB; convert to BGR when cv2 is available.
            try:
                import cv2

                np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
            except Exception:
                pass

            pages.append(np_image)

    return IngestedDocument(
        pages=pages,
        page_count=page_count,
        ingested_pages=len(pages),
        source_type="pdf",
    )


def ingest_document(payload: bytes, filename: str, content_type: str | None) -> IngestedDocument:
    suffix = Path(filename).suffix.lower()
    is_pdf = content_type == "application/pdf" or suffix == ".pdf"

    if is_pdf:
        return _ingest_pdf(payload)

    page = _decode_image_bytes(payload)
    return IngestedDocument(
        pages=[page],
        page_count=1,
        ingested_pages=1,
        source_type="image",
    )
