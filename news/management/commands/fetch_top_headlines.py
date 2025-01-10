# news/management/commands/fetch_top_headlines.py

from django.core.management.base import BaseCommand
from news.utils import fetch_and_store_top_headlines

class Command(BaseCommand):
    help = 'Fetch and store top headlines from NewsAPI for all categories'

    def handle(self, *args, **options):
        self.stdout.write("Starting to fetch top headlines...")
        fetch_and_store_top_headlines(language='en', page_size=100)
        self.stdout.write("Finished fetching and storing headlines.")
