import argparse
import logging
from pathlib import Path

from pdf_worker.compressor import compress_pdf
from pdf_worker.logging_config import setup_logging
from pdf_worker.merger import merge_pdfs

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdf-worker",
        description="Compress/resize PDFs and optionally merge them.",
    )
    parser.add_argument(
        "--quality",
        choices=["low", "med", "high"],
        default="med",
        help="Compression quality preset (default: med)",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge all input PDFs into a single output file",
    )
    parser.add_argument(
        "--output-name",
        default="merged.pdf",
        help="Output filename when merging (default: merged.pdf)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        help="Override the DPI value from the quality preset",
    )
    parser.add_argument(
        "--order",
        nargs="+",
        metavar="FILE",
        help="Filenames (not paths) in desired merge order (e.g. --order b.pdf a.pdf)",
    )
    return parser


def main(argv: list[str] | None = None, base_dir: Path | None = None) -> None:
    args = build_parser().parse_args(argv)

    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent.parent

    setup_logging(base_dir)

    ingest_dir = base_dir / "runtime" / "ingest"
    output_dir = base_dir / "runtime" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.order:
        pdf_files = []
        for name in args.order:
            path = ingest_dir / name
            if path.exists():
                pdf_files.append(path)
            else:
                logger.error("Ordered file not found: %s", name)
        if not pdf_files:
            logger.warning("None of the ordered files were found in %s", ingest_dir)
            return
    else:
        pdf_files = sorted(ingest_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning("No PDF files found in %s", ingest_dir)
            return

    logger.info("Processing %d PDF(s) from %s", len(pdf_files), ingest_dir)

    # Compress each PDF
    compressed_paths: list[Path] = []
    for pdf_path in pdf_files:
        out_path = output_dir / pdf_path.name
        try:
            compress_pdf(pdf_path, out_path, quality=args.quality, dpi_override=args.dpi)
            compressed_paths.append(out_path)
        except Exception:
            logger.error("Failed to compress %s, skipping", pdf_path.name, exc_info=True)

    # Optionally merge
    if args.merge and compressed_paths:
        merge_output = output_dir / args.output_name
        try:
            merge_pdfs(compressed_paths, merge_output)
        except Exception:
            logger.error("Failed to merge PDFs", exc_info=True)


if __name__ == "__main__":
    main()
