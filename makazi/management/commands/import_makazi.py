import csv
from django.core.management.base import BaseCommand
from makazi.models import Scrape_MakaziListing
from django.utils.dateparse import parse_datetime


class Command(BaseCommand):
    help = "Import makazi.csv into Scrape_MakaziListing model"

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to makazi.csv'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        try:
            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    Scrape_MakaziListing.objects.update_or_create(
                        link=row['link'],   # unique field
                        defaults={
                            'title': row['title'],
                            'price': row['price'],
                            'location': row['location'],
                            'description': row['description'],
                            'main_image_url': row['main_image_url'],
                            'scraped_at': parse_datetime(row['scraped_at']),

                            # extra model fields — set default values
                            'property_type': '',
                            'bedrooms': None,
                            'bathrooms': None,
                            'area_sqft': None,
                            'is_featured': False,
                            'is_verified': False,
                        }
                    )

            self.stdout.write(self.style.SUCCESS("Import Completed Successfully!"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("File not found. Check the path of makazi.csv"))
#python manage.py import_makazi makazi.csv