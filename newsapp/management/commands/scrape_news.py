
from django.core.management.base import BaseCommand
from news.scrapers.news_scraper import main as scrape_main

class Command(BaseCommand):
    help = "Scrape latest news"

    def handle(self, *args, **options):
        scrape_main()

