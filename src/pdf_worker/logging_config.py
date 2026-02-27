import logging.config
from pathlib import Path

import yaml


def setup_logging(base_dir: Path | None = None) -> None:
    """Load logging configuration from config/logging.yml."""
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent.parent

    config_path = base_dir / "config" / "logging.yml"
    logs_dir = base_dir / "runtime" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Resolve log file path relative to base_dir
    config["handlers"]["file"]["filename"] = str(logs_dir / "pdf_worker.log")

    logging.config.dictConfig(config)
