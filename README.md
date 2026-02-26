# Client Insight Newsfeed

A lightweight Python project that reads client data from JSON, processes it, and generates a newsfeed HTML report. The repository contains scripts for scraping, transforming, and rendering client information.

## Project Structure

```
config.yaml
README.md
DESIGN.md
requirements.txt

data/
    clients.json            # sample data file with client records
output/                     # generated output files (e.g. newsfeed HTML per company)
src/
    generator.py            # template-based HTML generator
    main.py                 # entry point, orchestrates workflow
    processor.py            # transforms and filters client data using an LLM
    scraper.py              # utilities to fetch or scrape data
    setup.py                # initialisation helpers (e.g. file readers)
templates/
    newsfeed_template.html  # Jinja2 HTML template for reports
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- [`venv`](https://docs.python.org/3/library/venv.html) or another virtual environment tool

### Installation

```bash
cd client-insight-newsfeed
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### Configuration

`config.yaml` holds the OpenAI information in the format
```
openai:
    api_key: ""
    model: ""
```

### Usage

Run the main script:

```bash
python src/main.py
```

This will produce HTML files under `output/` based on `templates/newsfeed_template.html`.

### Testing

Run the test suite:

```bash
python -m pytest tests/
```

Use `-v` for verbose output:

```bash
python -m pytest tests/ -v
```
