import io
import logging
from pathlib import Path

import pikepdf
from PIL import Image

logger = logging.getLogger(__name__)

QUALITY_PRESETS = {
    "low": {"dpi": 72, "jpeg_quality": 30},
    "med": {"dpi": 150, "jpeg_quality": 60},
    "high": {"dpi": 300, "jpeg_quality": 85},
}


def compress_pdf(input_path: Path, output_path: Path, quality: str = "med", dpi_override: int | None = None) -> Path:
    """Compress a PDF by resampling and recompressing embedded images."""
    preset = QUALITY_PRESETS[quality]
    target_dpi = dpi_override if dpi_override is not None else preset["dpi"]
    jpeg_quality = preset["jpeg_quality"]

    logger.info("Compressing %s with quality=%s, dpi=%d, jpeg_q=%d",
                input_path.name, quality, target_dpi, jpeg_quality)

    try:
        pdf = pikepdf.open(input_path)
    except Exception:
        logger.error("Failed to open %s", input_path)
        raise

    for page_num, page in enumerate(pdf.pages, 1):
        _compress_page_images(pdf, page, page_num, target_dpi, jpeg_quality)

    pdf.save(output_path, linearize=True)
    pdf.close()

    logger.info("Saved compressed PDF to %s", output_path)
    return output_path


def _compress_page_images(
    pdf: pikepdf.Pdf,
    page: pikepdf.Page,
    page_num: int,
    target_dpi: int,
    jpeg_quality: int,
) -> None:
    """Find and recompress images on a single page."""
    resources = page.get("/Resources", {})
    xobjects = resources.get("/XObject", {})

    for name, obj_ref in xobjects.items():
        try:
            obj = obj_ref
            if not isinstance(obj, pikepdf.Stream):
                continue
            if obj.get("/Subtype") != pikepdf.Name.Image:
                continue

            width = int(obj.get("/Width", 0))
            height = int(obj.get("/Height", 0))
            if width == 0 or height == 0:
                continue

            # Determine scale factor based on target DPI
            # Assume current images are at 300 DPI as baseline
            scale = target_dpi / 300
            new_w = max(1, int(width * scale))
            new_h = max(1, int(height * scale))

            # Use read_raw_bytes for streams pikepdf can't decode,
            # then fall back to read_bytes for uncompressed streams
            try:
                pdfimage = pikepdf.PdfImage(obj)
                img = pdfimage.as_pil_image()
            except Exception:
                try:
                    raw_data = obj.read_raw_bytes()
                    img = Image.open(io.BytesIO(raw_data))
                except Exception:
                    raw_data = obj.read_bytes()
                    img = Image.open(io.BytesIO(raw_data))

            img = img.resize((new_w, new_h), Image.LANCZOS)
            img = img.convert("RGB")

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
            compressed_data = buf.getvalue()

            obj.write(compressed_data, filter=pikepdf.Name.DCTDecode)
            obj["/Width"] = new_w
            obj["/Height"] = new_h
            obj["/ColorSpace"] = pikepdf.Name.DeviceRGB
            obj["/BitsPerComponent"] = 8

            logger.debug("Page %d: recompressed image %s (%dx%d -> %dx%d)",
                         page_num, name, width, height, new_w, new_h)

        except Exception:
            logger.warning("Page %d: failed to process image %s, skipping",
                           page_num, name, exc_info=True)
