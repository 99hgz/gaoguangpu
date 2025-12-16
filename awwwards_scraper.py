"""Scrape Visit Site links from Awwwards website listing pages."""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, Iterable, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
)
LISTING_TEMPLATE = "https://www.awwwards.com/websites/?page={page}"
BASE_URL = "https://www.awwwards.com"


def fetch_html(url: str, *, timeout: int = 15) -> str:
    """Fetch HTML from a URL with headers that mimic a browser."""
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()
    return response.text


def extract_site_links(listing_html: str) -> List[str]:
    """Extract unique site detail page URLs from a listing page."""
    soup = BeautifulSoup(listing_html, "html.parser")
    links = []
    for anchor in soup.select('a[href*="/sites/"]'):
        href = anchor.get("href")
        if not href or "/sites/" not in href:
            continue
        absolute = urljoin(BASE_URL, href.split("?")[0])
        links.append(absolute)
    # preserve order while removing duplicates
    seen = set()
    unique_links = []
    for link in links:
        if link not in seen:
            seen.add(link)
            unique_links.append(link)
    return unique_links


def extract_visit_site(detail_html: str) -> Optional[str]:
    """Return the Visit Site href from a site detail page, if present."""
    soup = BeautifulSoup(detail_html, "html.parser")
    button = soup.find("a", string=lambda text: text and text.strip().lower() == "visit site")
    if button:
        return button.get("href")
    return None


def scrape_awwwards(
    pages: Iterable[int], *, delay: float = 0.0, max_sites: Optional[int] = None
) -> Dict[str, Optional[str]]:
    """Scrape Visit Site links keyed by site detail page URLs for the given pages."""

    results: Dict[str, Optional[str]] = {}
    for page in pages:
        listing_url = LISTING_TEMPLATE.format(page=page)
        listing_html = fetch_html(listing_url)
        for site_url in extract_site_links(listing_html):
            if site_url in results:
                continue
            try:
                detail_html = fetch_html(site_url)
                results[site_url] = extract_visit_site(detail_html)
            except requests.RequestException:
                results[site_url] = None
            if delay:
                time.sleep(delay)
            if max_sites and len(results) >= max_sites:
                return results
    return results


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-page", type=int, default=1, help="First page to scrape (inclusive).")
    parser.add_argument(
        "--end-page",
        type=int,
        help="Last page to scrape (inclusive). Defaults to start page when omitted.",
    )
    parser.add_argument("--delay", type=float, default=0.0, help="Seconds to sleep between site requests.")
    parser.add_argument(
        "--max-sites", type=int, help="Optional cap on the total number of site pages to fetch."
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Optional path to write JSON results. Prints to stdout when omitted.",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    end_page = args.end_page if args.end_page is not None else args.start_page
    if args.start_page < 1 or end_page < args.start_page:
        print("Invalid page range provided.", file=sys.stderr)
        return 1

    pages = range(args.start_page, end_page + 1)
    results = scrape_awwwards(pages, delay=args.delay, max_sites=args.max_sites)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(results, fh, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
