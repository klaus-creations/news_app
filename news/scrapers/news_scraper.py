
import logging
import argparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_page(self, url):
        """Fetch HTML content with error handling."""
        try:
            logger.info(f"Fetching URL: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def parse_articles(self, html):
        """Extract articles from HTML (Hacker News example)."""
        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        for item in soup.select('.athing'):
            title_tag = item.select_one('.titleline a')
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            url = title_tag['href']
            summary = f"Read more about {title}..."
            publication_date = datetime.now().date()  # Dummy date

            articles.append({
                "title": title,
                "publication_date": publication_date,
                "summary": summary,
                "source_url": url,
            })

        return articles

    def scrape_paginated(self, pages=1, limit_per_page=10, keyword=None, category=None):
        """Scrape multiple pages, filter by keyword or category."""
        url = self.base_url

        # Apply category if provided (depends on site structure)
        if category:
            url = urljoin(self.base_url, category + "/")

        all_articles = []

        for _ in range(pages):
            html = self.fetch_page(url)
            if not html:
                break

            articles = self.parse_articles(html)

            # Filter by keyword if provided
            if keyword:
                articles = [a for a in articles if keyword.lower() in a['title'].lower()]

            all_articles.extend(articles[:limit_per_page])

            # Find next page link
            soup = BeautifulSoup(html, 'html.parser')
            more_link = soup.select_one('a.morelink')
            if more_link:
                next_url = more_link.get('href')
                if not next_url.startswith('http'):
                    next_url = urljoin(self.base_url, next_url)
                url = next_url
            else:
                break

        return all_articles


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="News Scraper with pagination & filters")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to scrape")
    parser.add_argument("--limit", type=int, default=10, help="Articles per page")
    parser.add_argument("--keyword", type=str, help="Filter by keyword in title")
    parser.add_argument("--category", type=str, help="News category (depends on site)")
    args = parser.parse_args()

    scraper = NewsScraper("https://news.ycombinator.com/")
    articles = scraper.scrape_paginated(
        pages=args.pages,
        limit_per_page=args.limit,
        keyword=args.keyword,
        category=args.category
    )

    logger.info(f"Scraped {len(articles)} articles")
    for i, art in enumerate(articles, start=1):
        print(f"{i}. {art['title']} ({art['publication_date']})")
        print(f"   Summary: {art['summary']}")
        print(f"   URL: {art['source_url']}\n")

