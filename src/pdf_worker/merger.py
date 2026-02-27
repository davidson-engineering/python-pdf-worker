import logging
from pathlib import Path

import pikepdf

logger = logging.getLogger(__name__)


def merge_pdfs(input_paths: list[Path], output_path: Path) -> Path:
    """Merge multiple PDFs into a single output file."""
    if not input_paths:
        raise ValueError("No PDFs to merge")

    logger.info("Merging %d PDFs into %s", len(input_paths), output_path.name)

    merged = pikepdf.Pdf.new()

    for path in input_paths:
        logger.debug("Appending %s", path.name)
        src = pikepdf.open(path)
        merged.pages.extend(src.pages)

    merged.save(output_path)
    merged.close()

    logger.info("Saved merged PDF to %s", output_path)
    return output_path
