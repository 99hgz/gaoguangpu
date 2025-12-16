# Awwwards Visit Site scraper

A simple Python script for scraping the external "Visit Site" links from Awwwards listing pages (e.g. `https://www.awwwards.com/websites/?page={num}`).

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Scrape a single page and print results to stdout:

```bash
python awwwards_scraper.py --start-page 1
```

Scrape multiple pages and write the output to JSON:

```bash
python awwwards_scraper.py --start-page 1 --end-page 3 --output results.json
```

Optional flags:

- `--delay` – seconds to sleep between each site request to be polite to the server (default `0`).
- `--max-sites` – limit how many site detail pages are fetched (useful for quick tests).

The script outputs a JSON object where keys are Awwwards site detail URLs and values are the corresponding "Visit Site" hrefs (or `null` if none is found).
