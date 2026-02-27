import pytest

from pdf_worker.compressor import compress_pdf


class TestCompress:
    @pytest.mark.parametrize("quality", ["low", "med", "high"])
    def test_compress_produces_output(self, sample_pdf, workspace, quality):
        output = workspace / "runtime" / "output" / "out.pdf"
        compress_pdf(sample_pdf, output, quality=quality)
        assert output.exists()
        assert output.stat().st_size > 0

    def test_low_quality_smaller_than_high(self, sample_pdf, workspace):
        out_low = workspace / "runtime" / "output" / "low.pdf"
        out_high = workspace / "runtime" / "output" / "high.pdf"
        compress_pdf(sample_pdf, out_low, quality="low")
        compress_pdf(sample_pdf, out_high, quality="high")
        assert out_low.stat().st_size <= out_high.stat().st_size

    def test_corrupt_input_raises(self, workspace):
        bad_pdf = workspace / "runtime" / "ingest" / "bad.pdf"
        bad_pdf.write_bytes(b"not a pdf")
        output = workspace / "runtime" / "output" / "bad_out.pdf"
        with pytest.raises(Exception):
            compress_pdf(bad_pdf, output)

    def test_empty_input_raises(self, workspace):
        empty_pdf = workspace / "runtime" / "ingest" / "empty.pdf"
        empty_pdf.write_bytes(b"")
        output = workspace / "runtime" / "output" / "empty_out.pdf"
        with pytest.raises(Exception):
            compress_pdf(empty_pdf, output)
