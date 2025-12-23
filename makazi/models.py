# makazi/models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
import re            # <--- ONGOZA HAPA


class Scrape_MakaziListing(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    link = models.URLField(unique=True)
    price = models.CharField(max_length=100)
    location = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    main_image_url = models.URLField(blank=True, null=True)
    posted_on_fb = models.DateTimeField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    
    # Additional fields for filtering
    property_type = models.CharField(max_length=50, blank=True, db_index=True)
    bedrooms = models.IntegerField(null=True, blank=True, db_index=True)
    bathrooms = models.IntegerField(null=True, blank=True)
    area_sqft = models.IntegerField(null=True, blank=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    digits_price = models.CharField(max_length=50, blank=True, db_index=True)

    
    @property
    def numeric_price(self):
        """Extract numeric price for filtering and sorting"""
        if not self.price:
            return 0
        
        try:
            # Remove all non-digit characters
            price_str = re.sub(r'[^\d]', '', str(self.price))
            if price_str:
                return int(price_str)
            return 0
        except (ValueError, TypeError):
            return 0

    def save(self, *args, **kwargs):
        # Extract digits from price
        if self.price:
            self.digits_price = re.sub(r'[^0-9]', '', str(self.price))
        super().save(*args, **kwargs)
    
    class Meta:
        # Add indexes for better performance
        indexes = [
            models.Index(fields=['title', 'location']),
            models.Index(fields=['property_type']),
            models.Index(fields=['bedrooms']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['scraped_at']),
        ]
        ordering = ['-scraped_at']

    def __str__(self):
        return self.title

    def get_slug_id(self):
        return f"{slugify(self.title)}-{self.id}"

    def get_absolute_url(self):
        return reverse('makazi:property_detail', kwargs={'slug_id': self.get_slug_id()})
    
    def get_price_number(self):
        """Extract numeric price for sorting"""
        import re
        price_str = str(self.price)
        numbers = re.findall(r'\d+', price_str)
        if numbers:
            return int(''.join(numbers))
        return 0
    
    def get_short_description(self):
        """Get truncated description"""
        if len(self.description) > 150:
            return self.description[:150] + '...'
        return self.description

class ContactMessage(models.Model):
    listing = models.ForeignKey(Scrape_MakaziListing, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.name} for {self.listing.title}"





# makazi/models.py - Ongeza baada ya Scrape_MakaziListing
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Apartment(models.Model):
    APARTMENT_TYPES = [
        ('studio', 'Studio'),
        ('1bed', '1 Bedroom'),
        ('2bed', '2 Bedrooms'),
        ('3bed', '3 Bedrooms'),
        ('penthouse', 'Penthouse'),
        ('duplex', 'Duplex'),
    ]
    
    AMENITIES_CHOICES = [
        ('wifi', 'Wi-Fi'),
        ('parking', 'Parking'),
        ('pool', 'Swimming Pool'),
        ('gym', 'Gym'),
        ('security', '24/7 Security'),
        ('elevator', 'Elevator'),
        ('ac', 'Air Conditioning'),
        ('heating', 'Heating'),
        ('laundry', 'Laundry Facilities'),
        ('balcony', 'Balcony'),
        ('garden', 'Garden'),
        ('playground', 'Playground'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200, db_index=True)
    address = models.TextField()
    
    # Apartment Details
    apartment_type = models.CharField(max_length=50, choices=APARTMENT_TYPES)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maintenance_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Specifications
    total_rooms = models.IntegerField(default=1)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    area_sqft = models.IntegerField()
    floor_number = models.IntegerField(default=1)
    total_floors = models.IntegerField(default=1)
    
    # Amenities (ManyToMany for multiple selections)
    amenities = models.JSONField(default=list, blank=True)
    
    # Images
    main_image = models.ImageField(upload_to='apartments/main/', null=True, blank=True)
    image_1 = models.ImageField(upload_to='apartments/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='apartments/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='apartments/', null=True, blank=True)
    image_4 = models.ImageField(upload_to='apartments/', null=True, blank=True)
    
    # Contact Information
    owner_name = models.CharField(max_length=100)
    owner_phone = models.CharField(max_length=20)
    owner_email = models.EmailField(blank=True)
    
    # Status
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Dates
    # available_from = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Location coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['price_per_month']),
            models.Index(fields=['is_available']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.location}"
    
    def get_all_images(self):
        """Get all images for the apartment"""
        images = []
        if self.main_image:
            images.append(self.main_image.url)
        if self.image_1:
            images.append(self.image_1.url)
        if self.image_2:
            images.append(self.image_2.url)
        if self.image_3:
            images.append(self.image_3.url)
        if self.image_4:
            images.append(self.image_4.url)
        return images
    
    def get_total_price(self):
        """Calculate total price including all fees"""
        return self.price_per_month + self.security_deposit + self.maintenance_fee
    
    def get_short_description(self):
        """Get truncated description"""
        if len(self.description) > 150:
            return self.description[:150] + '...'
        return self.description

class ApartmentBooking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Booking Details
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    duration_months = models.IntegerField(default=1)
    number_of_guests = models.IntegerField(default=1)
    
    # Payment Information
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maintenance_fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    payment_status = models.BooleanField(default=False)
    
    # Special Requests
    special_requests = models.TextField(blank=True)
    
    # Dates
    booking_date = models.DateTimeField(auto_now_add=True)
    confirmation_date = models.DateTimeField(null=True, blank=True)
    cancellation_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-booking_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['booking_date']),
        ]
    
    def __str__(self):
        return f"Booking #{self.id} - {self.apartment.title}"
    
    def calculate_total_amount(self):
        """Calculate total booking amount"""
        rent_total = self.monthly_rent * self.duration_months
        return rent_total + self.security_deposit_paid + self.maintenance_fee_paid
    
    def save(self, *args, **kwargs):
        # Auto-calculate total amount if not set
        if not self.total_amount:
            self.total_amount = self.calculate_total_amount()
        super().save(*args, **kwargs)

class ApartmentReview(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    reviewer_email = models.EmailField(blank=True)
    
    # Rating (1-5 stars)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Review
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['apartment']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"Review by {self.reviewer_name} - {self.rating} stars"