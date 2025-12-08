# makazi/context_processors.py
from django.db.models import Count
from .models import Scrape_MakaziListing  # Hii ndiyo muhimu!

def global_data(request):
    try:
        popular_locations = Scrape_MakaziListing.objects.values(
            'location'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:8]
    except:
        popular_locations = []
    
    return {
        'popular_locations': popular_locations,
        'site_name': 'NyumbaFasta',
        'site_description': 'Pata nyumba na makao bora Tanzania',
    }