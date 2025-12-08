import csv
from datetime import datetime
from makazi.models import Scrape_MakaziListing  # badilisha app jina

with open('makazi.csv', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    for row in reader:
        Scrape_MakaziListing.objects.update_or_create(
            link=row['link'],   # unique field
            defaults={
                'title': row['title'],
                'price': row['price'],
                'location': row['location'],
                'description': row['description'],
                'main_image_url': row.get('main_image_url') or None,
                'posted_on_fb': row.get('posted_on_fb') or None,
                'property_type': row.get('property_type', ''),
                'bedrooms': int(row['bedrooms']) if row.get('bedrooms') else None,
                'bathrooms': int(row['bathrooms']) if row.get('bathrooms') else None,
                'area_sqft': int(row['area_sqft']) if row.get('area_sqft') else None,
                'is_featured': row.get('is_featured', 'False').lower() == 'true',
                'is_verified': row.get('is_verified', 'False').lower() == 'true',
            }
        )

print("Import Completed Successfully!")
