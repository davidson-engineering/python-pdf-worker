import io
from pathlib import Path

import pikepdf
import pytest
from PIL import Image


@pytest.fixture
def workspace(tmp_path):
    """Create a temporary workspace with ingest/output/logs dirs and a logging config."""
    ingest = tmp_path / "runtime" / "ingest"
    output = tmp_path / "runtime" / "output"
    logs = tmp_path / "runtime" / "logs"
    config_dir = tmp_path / "config"

    for d in (ingest, output, logs, config_dir):
        d.mkdir(parents=True)

    # Write a logging config pointing to the tmp logs dir
    config_dir.joinpath("logging.yml").write_text(f"""\
version: 1
disable_existing_loggers: false
formatters:
  standard:
    format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout
  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: standard
    filename: {logs / 'pdf_worker.log'}
    maxBytes: 5242880
    backupCount: 3
root:
  level: DEBUG
  handlers: [console, file]
""")

    return tmp_path


@pytest.fixture
def sample_pdf(workspace):
    """Create a sample PDF with an embedded JPEG image in the ingest dir."""
    ingest = workspace / "runtime" / "ingest"
    pdf_path = ingest / "sample.pdf"
    _create_pdf_with_image(pdf_path, width=600, height=800)
    return pdf_path


def _create_pdf_with_image(path: Path, width: int = 600, height: int = 800) -> None:
    """Generate a minimal PDF containing one JPEG image."""
    img = Image.new("RGB", (width, height), color="blue")
    img_buf = io.BytesIO()
    img.save(img_buf, format="JPEG", quality=95)
    img_data = img_buf.getvalue()

    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page(page_size=(width, height))
    page = pdf.pages[0]

    image_stream = pikepdf.Stream(pdf, img_data)
    image_stream["/Type"] = pikepdf.Name.XObject
    image_stream["/Subtype"] = pikepdf.Name.Image
    image_stream["/Width"] = width
    image_stream["/Height"] = height
    image_stream["/ColorSpace"] = pikepdf.Name.DeviceRGB
    image_stream["/BitsPerComponent"] = 8
    image_stream["/Filter"] = pikepdf.Name.DCTDecode

    page_resources = pikepdf.Dictionary({"/XObject": pikepdf.Dictionary({"/Im0": image_stream})})
    page["/Resources"] = pdf.make_indirect(page_resources)

    # Add a content stream that draws the image
    content = f"q {width} 0 0 {height} 0 0 cm /Im0 Do Q"
    page["/Contents"] = pdf.make_indirect(pikepdf.Stream(pdf, content.encode()))

    pdf.save(path)
    pdf.close()
