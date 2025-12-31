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







# makazi/views.py - Ongeza baada ya dashboard function
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Apartment, ApartmentBooking, ApartmentReview
from .forms import ApartmentFilterForm, ApartmentBookingForm, ApartmentReviewForm

def apartments_list(request):
    """List all apartments with filtering"""
    apartments = Apartment.objects.filter(is_available=True)
    
    # Initialize filter form
    filter_form = ApartmentFilterForm(request.GET)
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        
        # Location filter
        if data.get('location'):
            apartments = apartments.filter(
                Q(location__icontains=data['location']) |
                Q(address__icontains=data['location'])
            )
        
        # Apartment type filter
        if data.get('apartment_type'):
            apartments = apartments.filter(apartment_type=data['apartment_type'])
        
        # Price range filter
        if data.get('min_price'):
            apartments = apartments.filter(price_per_month__gte=data['min_price'])
        
        if data.get('max_price'):
            apartments = apartments.filter(price_per_month__lte=data['max_price'])
        
        # Bedrooms filter
        if data.get('bedrooms'):
            if data['bedrooms'] == '4':
                apartments = apartments.filter(bedrooms__gte=4)
            else:
                try:
                    bedrooms = int(data['bedrooms'])
                    apartments = apartments.filter(bedrooms=bedrooms)
                except ValueError:
                    pass
        
        # Amenities filter
        if data.get('amenities'):
            for amenity in data['amenities']:
                apartments = apartments.filter(amenities__contains=amenity)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['price_per_month', '-price_per_month', 'created_at', '-created_at', 
                   'bedrooms', '-bedrooms', 'area_sqft', '-area_sqft']
    
    if sort_by in valid_sorts:
        apartments = apartments.order_by(sort_by)
    else:
        apartments = apartments.order_by('-created_at')
    
    # Get featured apartments
    featured_apartments = apartments.filter(is_featured=True)[:3]
    
    # Get popular locations
    popular_locations = Apartment.objects.values('location').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Pagination
    paginator = Paginator(apartments, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'apartments': page_obj,
        'featured_apartments': featured_apartments,
        'filter_form': filter_form,
        'popular_locations': popular_locations,
        'total_apartments': apartments.count(),
        'sort_by': sort_by,
    }
    
    return render(request, 'apartments/list.html', context)

def apartment_detail(request, pk):
    """Apartment detail page with booking form"""
    apartment = get_object_or_404(Apartment, pk=pk, is_available=True)
    
    # Get similar apartments
    similar_apartments = Apartment.objects.filter(
        Q(location__icontains=apartment.location) |
        Q(apartment_type=apartment.apartment_type)
    ).exclude(id=apartment.id).filter(is_available=True).order_by('?')[:4]
    
    # Get reviews
    reviews = apartment.reviews.filter(is_approved=True).order_by('-created_at')[:10]
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Booking form
    booking_form = ApartmentBookingForm()
    
    # Review form
    review_form = ApartmentReviewForm()
    
    # Calculate dates for booking
    import datetime
    min_date = datetime.date.today().isoformat()
    max_date = (datetime.date.today() + datetime.timedelta(days=365)).isoformat()
    
    # Calculate total price breakdown
    total_price = apartment.get_total_price()
    
    if request.method == 'POST':
        if 'book_now' in request.POST:
            booking_form = ApartmentBookingForm(request.POST)
            if booking_form.is_valid():
                booking = booking_form.save(commit=False)
                booking.apartment = apartment
                booking.monthly_rent = apartment.price_per_month
                booking.security_deposit_paid = apartment.security_deposit
                booking.maintenance_fee_paid = apartment.maintenance_fee
                booking.check_out_date = booking.check_in_date + datetime.timedelta(days=30 * booking.duration_months)
                booking.total_amount = booking.calculate_total_amount()
                
                booking.save()
                messages.success(request, 'Booking request submitted successfully! We will contact you shortly.')
                return redirect('makazi:apartment_detail', pk=apartment.pk)
        
        elif 'submit_review' in request.POST:
            review_form = ApartmentReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.apartment = apartment
                review.save()
                messages.success(request, 'Review submitted for approval. Thank you!')
                return redirect('makazi:apartment_detail', pk=apartment.pk)
    
    context = {
        'apartment': apartment,
        'similar_apartments': similar_apartments,
        'reviews': reviews,
        'average_rating': average_rating,
        'booking_form': booking_form,
        'review_form': review_form,
        'min_date': min_date,
        'max_date': max_date,
        'total_price': total_price,
    }
    
    return render(request, 'apartments/detail.html', context)

@login_required
def my_bookings(request):
    """View user's bookings"""
    bookings = ApartmentBooking.objects.filter(customer_email=request.user.email).order_by('-booking_date')
    
    context = {
        'bookings': bookings,
    }
    
    return render(request, 'apartments/my_bookings.html', context)

def apartment_search(request):
    """Search apartments API"""
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    
    apartments = Apartment.objects.filter(is_available=True)
    
    if query:
        apartments = apartments.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )
    
    if location:
        apartments = apartments.filter(location__icontains=location)
    
    # Limit results
    apartments = apartments[:10]
    
    data = []
    for apartment in apartments:
        data.append({
            'id': apartment.id,
            'title': apartment.title,
            'location': apartment.location,
            'price': float(apartment.price_per_month),
            'type': apartment.get_apartment_type_display(),
            'bedrooms': apartment.bedrooms,
            'image': apartment.main_image.url if apartment.main_image else '',
            'url': f"/apartments/{apartment.id}/"
        })
    
    return JsonResponse({'apartments': data})

# Ongeza URLs za apartments kwenye urls.py



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Hostel, HostelBooking, HostelReview  # ONDOA 'Room' KUTOKA HAPA
from .forms import HostelBookingForm, HostelReviewForm, HostelFilterForm

def hostels_list(request):
    """List all hostels with filtering"""
    hostels = Hostel.objects.filter(is_available=True)
    
    # Initialize filter form
    filter_form = HostelFilterForm(request.GET)
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        
        # University filter
        if data.get('university'):
            hostels = hostels.filter(
                Q(university__icontains=data['university']) |
                Q(location__icontains=data['university'])
            )
        
        # Hostel type filter
        if data.get('hostel_type'):
            hostels = hostels.filter(hostel_type=data['hostel_type'])
        
        # Gender filter
        if data.get('gender_allowed'):
            hostels = hostels.filter(gender_allowed=data['gender_allowed'])
        
        # Price range filter
        if data.get('min_price'):
            hostels = hostels.filter(price_per_semester__gte=data['min_price'])
        
        if data.get('max_price'):
            hostels = hostels.filter(price_per_semester__lte=data['max_price'])
        
        # Amenities filter
        if data.get('amenities'):
            for amenity in data['amenities']:
                hostels = hostels.filter(amenities__contains=amenity)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['price_per_semester', '-price_per_semester', 'created_at', '-created_at']
    
    if sort_by in valid_sorts:
        hostels = hostels.order_by(sort_by)
    else:
        hostels = hostels.order_by('-created_at')
    
    # Get featured hostels
    featured_hostels = hostels.filter(is_featured=True)[:3]
    
    # Get popular universities
    popular_universities = Hostel.objects.values('university').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Pagination
    paginator = Paginator(hostels, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'hostels': page_obj,
        'featured_hostels': featured_hostels,
        'filter_form': filter_form,
        'popular_universities': popular_universities,
        'total_hostels': hostels.count(),
        'sort_by': sort_by,
    }
    
    return render(request, 'hostels/list.html', context)

def hostel_detail(request, pk):
    """Hostel detail page with booking form"""
    hostel = get_object_or_404(Hostel, pk=pk, is_available=True)
    
    # Get similar hostels (ONDOA 'available_rooms' QUERY)
    similar_hostels = Hostel.objects.filter(
        Q(university__icontains=hostel.university) |
        Q(location__icontains=hostel.location)
    ).exclude(id=hostel.id).filter(is_available=True).order_by('?')[:3]
    
    # Get reviews
    reviews = hostel.reviews.filter(is_approved=True).order_by('-created_at')[:10]
    
    # Calculate average ratings
    avg_ratings = {
        'overall': reviews.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0,
        'cleanliness': reviews.aggregate(Avg('cleanliness'))['cleanliness__avg'] or 0,
        'security': reviews.aggregate(Avg('security'))['security__avg'] or 0,
        'facilities': reviews.aggregate(Avg('facilities'))['facilities__avg'] or 0,
        'management': reviews.aggregate(Avg('management'))['management__avg'] or 0,
    }
    
    # Booking form
    booking_form = HostelBookingForm(initial={
        'academic_year': hostel.academic_year,
        'semester': hostel.semester,
    })
    
    # Review form
    review_form = HostelReviewForm()
    
    # Calculate dates for template
    import datetime
    min_date = datetime.date.today().isoformat()
    max_date = (datetime.date.today() + datetime.timedelta(days=365)).isoformat()
    
    if request.method == 'POST':
        if 'book_now' in request.POST:
            booking_form = HostelBookingForm(request.POST)
            if booking_form.is_valid():
                booking = booking_form.save(commit=False)
                booking.hostel = hostel
                booking.academic_year = hostel.academic_year
                booking.semester = hostel.semester
                
                # Calculate total amount based on booking type
                if booking.booking_type == 'semester':
                    booking.total_amount = hostel.price_per_semester + hostel.security_deposit + hostel.caution_money
                elif booking.booking_type == 'monthly':
                    booking.total_amount = (hostel.price_per_month * booking.duration_months) + hostel.security_deposit + hostel.caution_money
                else:  # academic year
                    booking.total_amount = (hostel.price_per_semester * 2) + hostel.security_deposit + hostel.caution_money
                
                # Auto-set check-out date
                booking.check_out_date = booking.check_in_date + datetime.timedelta(days=30 * booking.duration_months)
                
                # Auto-set payment deadline (2 weeks before check-in)
                booking.payment_deadline = booking.check_in_date - datetime.timedelta(days=14)
                
                # Link to user if authenticated
                if request.user.is_authenticated:
                    booking.student = request.user
                
                booking.save()
                
                # Update hostel occupancy
                hostel.current_occupancy += 1
                hostel.available_rooms = max(0, hostel.total_rooms - (hostel.current_occupancy // 4))
                hostel.save()
                
                messages.success(request, 'Booking submitted successfully! Please complete payment within 2 weeks.')
                return redirect('makazi:booking_confirmation', booking_id=booking.id)
        
        elif 'submit_review' in request.POST:
            review_form = HostelReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.hostel = hostel
                if request.user.is_authenticated:
                    review.student = request.user
                    review.is_verified_student = True
                review.save()
                messages.success(request, 'Review submitted for approval. Thank you!')
                return redirect('makazi:hostel_detail', pk=hostel.pk)
    
    context = {
        'hostel': hostel,
        'similar_hostels': similar_hostels,
        'reviews': reviews,
        'avg_ratings': avg_ratings,
        'booking_form': booking_form,
        'review_form': review_form,
        'min_date': min_date,
        'max_date': max_date,
    }
    
    return render(request, 'hostels/detail.html', context)

@login_required
def my_bookings(request):
    """View student's hostel bookings"""
    bookings = HostelBooking.objects.filter(
        Q(student_email=request.user.email) |
        Q(student=request.user)
    ).order_by('-booking_date')
    
    context = {'bookings': bookings}
    return render(request, 'hostels/my_bookings.html', context)

def booking_confirmation(request, booking_id):
    """Booking confirmation page with payment instructions"""
    booking = get_object_or_404(HostelBooking, id=booking_id)
    
    # Generate payment instructions for Tanzania
    payment_instructions = {
        'bank_name': 'CRDB Bank / NMB Bank',
        'account_name': f"{booking.hostel.name} Hostel Account",
        'account_number': '0123456789',
        'reference': f"HST{booking.id}",
        'mobile_money': {
            'vodacom': '*150*00#',
            'airtel': '*150*60#',
            'tigo': '*150*01#',
            'number': '0754123456'
        }
    }
    
    context = {
        'booking': booking,
        'payment_instructions': payment_instructions,
    }
    
    return render(request, 'hostels/booking_confirmation.html', context)

def university_hostels(request, university_name):
    """Filter hostels by specific university"""
    hostels = Hostel.objects.filter(
        Q(university__icontains=university_name) |
        Q(location__icontains=university_name),
        is_available=True
    )
    
    context = {
        'hostels': hostels,
        'university': university_name,
        'total_hostels': hostels.count(),
    }
    
    return render(request, 'hostels/university_hostels.html', context)

def search_hostels(request):
    """AJAX search for hostels"""
    query = request.GET.get('q', '')
    university = request.GET.get('university', '')
    
    hostels = Hostel.objects.filter(is_available=True)
    
    if query:
        hostels = hostels.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )
    
    if university:
        hostels = hostels.filter(university__icontains=university)
    
    hostels = hostels[:10]
    
    data = []
    for hostel in hostels:
        data.append({
            'id': hostel.id,
            'name': hostel.name,
            'university': hostel.university,
            'location': hostel.location,
            'price_per_semester': float(hostel.price_per_semester),
            'available_rooms': hostel.available_rooms,
            'hostel_type': hostel.get_hostel_type_display(),
        })
    
    return JsonResponse({'hostels': data})