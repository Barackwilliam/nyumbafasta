# makazi/filters.py
import django_filters
from .models import Scrape_MakaziListing

class PropertyFilter(django_filters.FilterSet):
    location = django_filters.CharFilter(
        field_name='location', 
        lookup_expr='icontains',
        label='Location'
    )
    
    property_type = django_filters.CharFilter(
        field_name='property_type',
        label='Property Type'
    )
    
    min_price = django_filters.CharFilter(
        field_name='price',
        lookup_expr='gte',
        label='Min Price'
    )
    
    max_price = django_filters.CharFilter(
        field_name='price',
        lookup_expr='lte',
        label='Max Price'
    )
    
    bedrooms = django_filters.NumberFilter(
        field_name='bedrooms',
        label='Bedrooms'
    )
    
    is_featured = django_filters.BooleanFilter(
        field_name='is_featured',
        label='Featured Only'
    )
    
    is_verified = django_filters.BooleanFilter(
        field_name='is_verified',
        label='Verified Only'
    )
    
    class Meta:
        model = Scrape_MakaziListing
        fields = ['location', 'property_type', 'bedrooms', 'is_featured', 'is_verified']