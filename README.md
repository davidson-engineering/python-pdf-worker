# PDF Worker

A CLI tool for compressing/resizing PDFs and optionally merging them into a single file.

## Installation

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

Place your PDF files in `runtime/ingest/`, then run:

```bash
uv run ppw [OPTIONS]
```

Or equivalently:

```bash
uv run python -m pdf_worker [OPTIONS]
```

Compressed files are written to `runtime/output/`. Logs are written to `runtime/logs/pdf_worker.log`.

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--quality {low,med,high}` | Compression quality preset | `med` |
| `--dpi DPI` | Override the DPI value from the quality preset | _(from preset)_ |
| `--merge` | Merge all processed PDFs into a single output file | off |
| `--output-name NAME` | Output filename when merging | `merged.pdf` |
| `--order FILE [FILE ...]` | Process/merge files in this order (filenames only, not paths) | alphabetical |

### Quality Presets

| Preset | Image DPI | JPEG Quality |
|--------|-----------|--------------|
| `low`  | 72        | 30           |
| `med`  | 150       | 60           |
| `high` | 300       | 85           |

The `--dpi` flag overrides the DPI from the selected preset while keeping its JPEG quality setting.

### Examples

Compress all PDFs at medium quality (default):

```bash
uv run ppw
```

Compress at low quality for smallest file size:

```bash
uv run ppw --quality low
```

Compress at high quality but with a custom DPI of 200:

```bash
uv run ppw --quality high --dpi 200
```

Compress and merge all PDFs into one file:

```bash
uv run ppw --merge
```

Merge with a custom output name and specific file order:

```bash
uv run ppw --merge --output-name combined.pdf --order chapter2.pdf chapter1.pdf appendix.pdf
```

## Development

Run the test suite:

```bash
uv run pytest
```
