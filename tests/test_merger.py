import pikepdf
import pytest

from conftest import _create_pdf_with_image
from pdf_worker.merger import merge_pdfs


class TestMerge:
    def test_merge_two_pdfs(self, workspace):
        ingest = workspace / "runtime" / "ingest"
        _create_pdf_with_image(ingest / "a.pdf")
        _create_pdf_with_image(ingest / "b.pdf")

        output = workspace / "runtime" / "output" / "merged.pdf"
        merge_pdfs([ingest / "a.pdf", ingest / "b.pdf"], output)

        merged = pikepdf.open(output)
        assert len(merged.pages) == 2
        merged.close()

    def test_merge_single_pdf(self, workspace):
        ingest = workspace / "runtime" / "ingest"
        _create_pdf_with_image(ingest / "only.pdf")

        output = workspace / "runtime" / "output" / "merged.pdf"
        merge_pdfs([ingest / "only.pdf"], output)
        assert output.exists()

    def test_merge_empty_list_raises(self, workspace):
        output = workspace / "runtime" / "output" / "merged.pdf"
        with pytest.raises(ValueError, match="No PDFs to merge"):
            merge_pdfs([], output)
