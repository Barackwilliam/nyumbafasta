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
    }
    return render(request, 'index.html', context)

def property_listings(request):
    """All listings with advanced filtering"""
    listings = Scrape_MakaziListing.objects.all()
    for l in listings:
        l._digits_price = re.sub(r'[^0-9]', '', str(l.price or ''))

    
    # Apply filters
    property_filter = PropertyFilter(request.GET, queryset=listings)
    filtered_listings = property_filter.qs
    
    # Sorting
    sort_by = request.GET.get('sort', '-scraped_at')
    if sort_by in ['price', '-price', 'bedrooms', '-bedrooms', 'area_sqft', '-area_sqft']:
        filtered_listings = filtered_listings.order_by(sort_by)
    else:
        filtered_listings = filtered_listings.order_by('-scraped_at')
    
    # Get unique values for filters
    locations = Scrape_MakaziListing.objects.values_list(
        'location', flat=True
    ).distinct().order_by('location')[:50]
    
    property_types = Scrape_MakaziListing.objects.values_list(
        'property_type', flat=True
    ).distinct().exclude(property_type='').order_by('property_type')
    
    # Pagination
    paginator = Paginator(filtered_listings, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'listings': page_obj,
        'listings': listings,
        'filter': property_filter,
        'locations': locations,
        'property_types': property_types,
        'sort_options': [
            ('-scraped_at', 'Newest First'),
            ('scraped_at', 'Oldest First'),
            ('price', 'Price: Low to High'),
            ('-price', 'Price: High to Low'),
            ('bedrooms', 'Bedrooms: Low to High'),
            ('-bedrooms', 'Bedrooms: High to Low'),
        ]
    }
    return render(request, 'listings.html', context)

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