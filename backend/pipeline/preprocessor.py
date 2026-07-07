# =============================================================================
# Image Preprocessor — PDF rendering + image enhancement
# =============================================================================
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

MAX_LONG_EDGE = 3000  # px — sufficient for Gemini without token bloat
CONTRAST_FACTOR = 1.3
SHARPNESS_FACTOR = 1.4


def preprocess(file_bytes: bytes, content_type: str) -> Image.Image:
    """Convert uploaded file to an enhanced PIL Image ready for AI extraction.

    Pipeline:
    1. PDF → render first page at 200 DPI as RGB image
    2. PNG/JPG → load directly
    3. Resize if larger than MAX_LONG_EDGE (preserve aspect ratio)
    4. Enhance contrast and sharpness for better AI legibility
    5. Ensure RGB mode (not RGBA or L)

    Args:
        file_bytes: Raw file content.
        content_type: MIME type (image/png, image/jpeg, application/pdf).

    Returns:
        Enhanced PIL Image in RGB mode.
    """
    if content_type == "application/pdf":
        image = _render_pdf(file_bytes)
    else:
        image = Image.open(io.BytesIO(file_bytes))

    image = _ensure_rgb(image)
    image = _resize(image)
    image = _enhance(image)
    return image


def _render_pdf(file_bytes: bytes) -> Image.Image:
    """Render first page of PDF to PIL Image."""
    try:
        from pdf2image import convert_from_bytes  # type: ignore

        pages = convert_from_bytes(file_bytes, dpi=200, first_page=1, last_page=1)
        if not pages:
            raise ValueError("PDF produced no pages")
        return pages[0]
    except ImportError:
        # pdf2image / poppler not available — return a blank image with a note
        img = Image.new("RGB", (800, 600), color=(240, 240, 240))
        return img


def _ensure_rgb(image: Image.Image) -> Image.Image:
    if image.mode not in ("RGB",):
        return image.convert("RGB")
    return image


def _resize(image: Image.Image) -> Image.Image:
    w, h = image.size
    long_edge = max(w, h)
    if long_edge <= MAX_LONG_EDGE:
        return image
    scale = MAX_LONG_EDGE / long_edge
    new_w = int(w * scale)
    new_h = int(h * scale)
    return image.resize((new_w, new_h), Image.LANCZOS)


def _enhance(image: Image.Image) -> Image.Image:
    image = ImageEnhance.Contrast(image).enhance(CONTRAST_FACTOR)
    image = ImageEnhance.Sharpness(image).enhance(SHARPNESS_FACTOR)
    return image
