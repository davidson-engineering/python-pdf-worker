import logging

from pdf_worker.logging_config import setup_logging


def test_logging_config_loads(workspace):
    setup_logging(base_dir=workspace)
    logger = logging.getLogger("pdf_worker.test")
    logger.info("test message")

    log_file = workspace / "runtime" / "logs" / "pdf_worker.log"
    assert log_file.exists()
    assert "test message" in log_file.read_text()
