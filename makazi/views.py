# makazi/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Scrape_MakaziListing, ContactMessage
from .filters import PropertyFilter
from .forms import ContactForm
import re


# Add at top of views.py
from django.conf import settings
import os

def get_default_image_url():
    """Get default image URL if exists, otherwise use data URI"""
    default_path = os.path.join(settings.STATIC_URL, 'images/default-property.jpg')
    full_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'default-property.jpg')
    
    if os.path.exists(full_path):
        return default_path
    else:
        # Return data URI for blue placeholder
        return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAwIiBoZWlnaHQ9IjYwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjNDM2MWVlIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIyNCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZTwvdGV4dD48L3N2Zz4='

def home(request):
    """Home page with featured and latest listings"""
    featured_listings = Scrape_MakaziListing.objects.filter(
        is_featured=True
    ).order_by('-scraped_at')[:8]
    
    latest_listings = Scrape_MakaziListing.objects.all().order_by('-scraped_at')[:12]
    
    # Get popular locations
    popular_locations = Scrape_MakaziListing.objects.values(
        'location'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:8]
    
    # Property type counts
    property_types = Scrape_MakaziListing.objects.values(
        'property_type'
    ).annotate(
        count=Count('id')
    ).exclude(property_type='')[:10]
    
    context = {
        'featured_listings': featured_listings,
        'latest_listings': latest_listings,
        'popular_locations': popular_locations,
        'property_types': property_types,
        'total_listings': Scrape_MakaziListing.objects.count(),
        'default_image_url': get_default_image_url(),

    }
    return render(request, 'index.html', context)

# def property_listings(request):
#     """All listings with advanced filtering"""
#     listings = Scrape_MakaziListing.objects.all()
#     for l in listings:
#         l._digits_price = re.sub(r'[^0-9]', '', str(l.price or ''))

    
#     # Apply filters
#     property_filter = PropertyFilter(request.GET, queryset=listings)
#     filtered_listings = property_filter.qs
    
#     # Sorting
#     sort_by = request.GET.get('sort', '-scraped_at')
#     if sort_by in ['price', '-price', 'bedrooms', '-bedrooms', 'area_sqft', '-area_sqft']:
#         filtered_listings = filtered_listings.order_by(sort_by)
#     else:
#         filtered_listings = filtered_listings.order_by('-scraped_at')
    
#     # Get unique values for filters
#     locations = Scrape_MakaziListing.objects.values_list(
#         'location', flat=True
#     ).distinct().order_by('location')[:50]
    
#     property_types = Scrape_MakaziListing.objects.values_list(
#         'property_type', flat=True
#     ).distinct().exclude(property_type='').order_by('property_type')
    
#     # Pagination
#     paginator = Paginator(filtered_listings, 16)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    
#     context = {
#         'listings': page_obj,
#         'listings': listings,
#         'filter': property_filter,
#         'locations': locations,
#         'property_types': property_types,
#         'sort_options': [
#             ('-scraped_at', 'Newest First'),
#             ('scraped_at', 'Oldest First'),
#             ('price', 'Price: Low to High'),
#             ('-price', 'Price: High to Low'),
#             ('bedrooms', 'Bedrooms: Low to High'),
#             ('-bedrooms', 'Bedrooms: High to Low'),
#         ]
#     }
#     return render(request, 'listings.html', context)



# makazi/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count, IntegerField
from django.db.models.functions import Cast, Substr
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.exceptions import ValidationError
from .models import Scrape_MakaziListing, ContactMessage
from .forms import ContactForm
import re

def extract_numeric_price(price_str):
    """Extract numeric value from price string"""
    if not price_str:
        return 0
    
    try:
        # Remove all non-digit characters except commas
        price_str = str(price_str).replace(',', '').strip()
        # Extract first number found
        numbers = re.findall(r'\d+', price_str)
        if numbers:
            return int(float(''.join(numbers)))
        return 0
    except (ValueError, TypeError):
        return 0

def property_listings(request):
    """All listings with advanced filtering - FIXED VERSION"""
    
    # Start with all listings
    queryset = Scrape_MakaziListing.objects.all()
    
    # Apply search filter
    search_query = request.GET.get('q', '').strip()
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(property_type__icontains=search_query)
        )
    
    # Apply location filter
    location = request.GET.get('location', '').strip()
    if location:
        queryset = queryset.filter(location__icontains=location)
    
    # Apply property type filter
    property_type = request.GET.get('property_type', '').strip()
    if property_type:
        queryset = queryset.filter(property_type__iexact=property_type)
    
    # Apply bedrooms filter
    bedrooms = request.GET.get('bedrooms', '').strip()
    if bedrooms:
        if bedrooms == '4':
            # 4+ bedrooms
            queryset = queryset.filter(bedrooms__gte=4)
        else:
            try:
                bedrooms_num = int(bedrooms)
                queryset = queryset.filter(bedrooms=bedrooms_num)
            except ValueError:
                pass
    
    # Apply price range filter
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    
    if min_price or max_price:
        # Create temporary numeric price field for filtering
        listings_with_price = []
        for listing in queryset:
            price_num = extract_numeric_price(listing.price)
            
            # Check if price falls within range
            include = True
            if min_price:
                try:
                    min_val = int(min_price)
                    if price_num < min_val:
                        include = False
                except ValueError:
                    pass
            
            if max_price:
                try:
                    max_val = int(max_price)
                    if price_num > max_val:
                        include = False
                except ValueError:
                    pass
            
            if include:
                listings_with_price.append(listing.id)
        
        queryset = queryset.filter(id__in=listings_with_price)
    
    # Apply featured filter
    is_featured = request.GET.get('is_featured', '').strip()
    if is_featured.lower() == 'true':
        queryset = queryset.filter(is_featured=True)
    
    # Apply verified filter
    is_verified = request.GET.get('is_verified', '').strip()
    if is_verified.lower() == 'true':
        queryset = queryset.filter(is_verified=True)
    
    # Apply has_images filter
    has_images = request.GET.get('has_images', '').strip()
    if has_images.lower() == 'true':
        queryset = queryset.exclude(main_image_url='').exclude(main_image_url__isnull=True)
    
    # Apply sorting
    sort_by = request.GET.get('sort', '-scraped_at')
    valid_sort_fields = ['-scraped_at', 'scraped_at', 'price', '-price', 'bedrooms', '-bedrooms', 'area_sqft', '-area_sqft']
    
    if sort_by in valid_sort_fields:
        if sort_by in ['price', '-price']:
            # Custom sorting for price strings
            listings_list = list(queryset)
            listings_list.sort(
                key=lambda x: extract_numeric_price(x.price),
                reverse=(sort_by == '-price')
            )
            # Create a new queryset from sorted list
            sorted_ids = [listing.id for listing in listings_list]
            # Preserve order using MySQL FIELD function or Python
            from django.db.models import Case, When
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_ids)])
            queryset = Scrape_MakaziListing.objects.filter(id__in=sorted_ids).order_by(preserved)
        else:
            queryset = queryset.order_by(sort_by)
    else:
        queryset = queryset.order_by('-scraped_at')
    
    # Pagination
    per_page = request.GET.get('per_page', '12')
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 12
    
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique values for filters
    locations = Scrape_MakaziListing.objects.values_list(
        'location', flat=True
    ).distinct().exclude(location='').order_by('location')[:50]
    
    property_types = Scrape_MakaziListing.objects.values_list(
        'property_type', flat=True
    ).distinct().exclude(property_type='').order_by('property_type')
    
    # Get popular locations
    popular_locations = Scrape_MakaziListing.objects.values(
        'location'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        'listings': page_obj,
        'locations': locations,
        'property_types': property_types,
        'popular_locations': popular_locations,
        'total_listings': queryset.count(),
        'request': request,  # Pass request to template for filter display
    }
    
    return render(request, 'listings.html', context)

# Other functions remain the same...

def property_detail(request, slug_id):
    """Property detail page"""
    # Extract ID from slug
    try:
        listing_id = int(slug_id.split('-')[-1])
        listing = get_object_or_404(Scrape_MakaziListing, id=listing_id)
    except (ValueError, IndexError):
        listing = get_object_or_404(Scrape_MakaziListing, slug_id=slug_id)
    
    # Get similar listings
    similar_listings = Scrape_MakaziListing.objects.filter(
        Q(location__icontains=listing.location.split(',')[0]) |
        Q(property_type=listing.property_type)
    ).exclude(id=listing.id).order_by('?')[:4]
    
    # Parse price for display
    price_info = parse_price_info(listing.price)
    
    # Contact form
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.listing = listing
            contact.save()
            return render(request, 'detail.html', {
                'listing': listing,
                'similar_listings': similar_listings,
                'price_info': price_info,
                'form': ContactForm(),
                'message_sent': True
            })
    else:
        form = ContactForm()
    
    context = {
        'listing': listing,
        'similar_listings': similar_listings,
        'price_info': price_info,
        'form': form,
    }
    return render(request, 'detail.html', context)

def parse_price_info(price_str):
    """Parse price string into displayable format"""
    if not price_str:
        return {'display': 'Bei: Tafadhali omba', 'numeric': 0}
    
    price_str = str(price_str).lower()
    
    # Extract numbers
    numbers = re.findall(r'[\d,]+', price_str)
    if not numbers:
        return {'display': price_str, 'numeric': 0}
    
    # Get the first number (usually the price)
    num_str = numbers[0].replace(',', '')
    try:
        price_num = int(float(num_str))
    except ValueError:
        return {'display': price_str, 'numeric': 0}
    
    # Format for display
    if price_num >= 1000000000:
        display = f"TSh {price_num/1000000000:.1f} Bilioni"
    elif price_num >= 1000000:
        display = f"TSh {price_num/1000000:.1f} Milioni"
    elif price_num >= 1000:
        display = f"TSh {price_num/1000:.0f},000"
    else:
        display = f"TSh {price_num:,}"
    
    # Add period if mentioned
    if 'month' in price_str or 'mwezi' in price_str:
        display += "/mwezi"
    elif 'year' in price_str or 'mwaka' in price_str:
        display += "/mwaka"
    
    return {'display': display, 'numeric': price_num}

def about(request):
    """About page"""
    return render(request, 'about.html')

def contact(request):
    """Contact page"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'contact.html', {'form': ContactForm(), 'success': True})
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

def contact_about_listing(request, listing_id):
    """Contact about specific listing"""
    listing = get_object_or_404(Scrape_MakaziListing, id=listing_id)
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.listing = listing
            contact.save()
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@require_GET
def filter_properties_api(request):
    """API endpoint for filtering properties"""
    filters = {}
    
    # Build filter dictionary
    if request.GET.get('location'):
        filters['location__icontains'] = request.GET.get('location')
    if request.GET.get('property_type'):
        filters['property_type'] = request.GET.get('property_type')
    if request.GET.get('min_price'):
        filters['price__gte'] = request.GET.get('min_price')
    if request.GET.get('max_price'):
        filters['price__lte'] = request.GET.get('max_price')
    if request.GET.get('bedrooms'):
        filters['bedrooms'] = request.GET.get('bedrooms')
    
    listings = Scrape_MakaziListing.objects.filter(**filters)[:20]
    
    data = []
    for listing in listings:
        data.append({
            'id': listing.id,
            'title': listing.title,
            'price': listing.price,
            'location': listing.location,
            'image_url': listing.main_image_url or '',
            'url': listing.get_absolute_url(),
            'bedrooms': listing.bedrooms,
            'property_type': listing.property_type,
        })
    
    return JsonResponse({'listings': data})

@require_GET
def search_properties_api(request):
    """API endpoint for search"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'results': []})
    
    listings = Scrape_MakaziListing.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(location__icontains=query) |
        Q(property_type__icontains=query)
    )[:10]
    
    results = []
    for listing in listings:
        results.append({
            'id': listing.id,
            'title': listing.title,
            'price': listing.price,
            'location': listing.location,
            'url': listing.get_absolute_url(),
        })
    
    return JsonResponse({'results': results})

def dashboard(request):
    """Admin dashboard"""
    if not request.user.is_staff:
        return redirect('home')
    
    stats = {
        'total_listings': Scrape_MakaziListing.objects.count(),
        'featured_listings': Scrape_MakaziListing.objects.filter(is_featured=True).count(),
        'verified_listings': Scrape_MakaziListing.objects.filter(is_verified=True).count(),
        'total_contacts': ContactMessage.objects.count(),
        'recent_contacts': ContactMessage.objects.order_by('-created_at')[:10],
        'locations_count': Scrape_MakaziListing.objects.values('location').distinct().count(),
    }
    
    return render(request, 'dashboard.html', {'stats': stats})

