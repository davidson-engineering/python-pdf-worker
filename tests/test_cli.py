import pikepdf

from conftest import _create_pdf_with_image
from pdf_worker.cli import build_parser, main


class TestArgParsing:
    def test_defaults(self):
        args = build_parser().parse_args([])
        assert args.quality == "med"
        assert args.merge is False
        assert args.output_name == "merged.pdf"

    def test_quality_low(self):
        args = build_parser().parse_args(["--quality", "low"])
        assert args.quality == "low"

    def test_quality_high(self):
        args = build_parser().parse_args(["--quality", "high"])
        assert args.quality == "high"

    def test_merge_flag(self):
        args = build_parser().parse_args(["--merge"])
        assert args.merge is True

    def test_output_name(self):
        args = build_parser().parse_args(["--merge", "--output-name", "combined.pdf"])
        assert args.output_name == "combined.pdf"

    def test_order_default_is_none(self):
        args = build_parser().parse_args([])
        assert args.order is None

    def test_order_flag(self):
        args = build_parser().parse_args(["--order", "b.pdf", "a.pdf"])
        assert args.order == ["b.pdf", "a.pdf"]


class TestEndToEnd:
    def test_compress_produces_output(self, sample_pdf, workspace):
        main(["--quality", "low"], base_dir=workspace)
        output = workspace / "runtime" / "output" / "sample.pdf"
        assert output.exists()
        assert output.stat().st_size > 0

    def test_compress_and_merge(self, sample_pdf, workspace):
        main(["--quality", "med", "--merge"], base_dir=workspace)
        output = workspace / "runtime" / "output" / "merged.pdf"
        assert output.exists()

    def test_no_pdfs_does_not_error(self, workspace):
        main(["--quality", "high"], base_dir=workspace)
        output_files = list((workspace / "runtime" / "output").glob("*.pdf"))
        assert output_files == []

    def test_order_controls_merge_sequence(self, workspace):
        ingest = workspace / "runtime" / "ingest"
        # Create two PDFs with different page sizes to distinguish them
        _create_pdf_with_image(ingest / "a.pdf", width=100, height=200)
        _create_pdf_with_image(ingest / "b.pdf", width=300, height=400)

        main(["--merge", "--order", "b.pdf", "a.pdf", "--quality", "low"], base_dir=workspace)
        merged = workspace / "runtime" / "output" / "merged.pdf"
        assert merged.exists()

        pdf = pikepdf.open(merged)
        # First page should be from b.pdf (300x400), second from a.pdf (100x200)
        p1_width = float(pdf.pages[0].mediabox[2])
        p2_width = float(pdf.pages[1].mediabox[2])
        assert p1_width > p2_width
        pdf.close()

    def test_order_skips_missing_files(self, workspace):
        ingest = workspace / "runtime" / "ingest"
        _create_pdf_with_image(ingest / "a.pdf")

        main(["--order", "missing.pdf", "a.pdf", "--quality", "low"], base_dir=workspace)
        output = workspace / "runtime" / "output" / "a.pdf"
        assert output.exists()
