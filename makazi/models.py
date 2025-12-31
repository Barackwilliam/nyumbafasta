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



from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

class Hostel(models.Model):
    HOSTEL_TYPES = [
        ('university', 'University Hostel'),
        ('private', 'Private Hostel'),
        ('college', 'College Hostel'),
        ('veta', 'VETA Hostel'),
        ('polytechnic', 'Polytechnic Hostel'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male Only'),
        ('female', 'Female Only'),
        ('mixed', 'Mixed'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    university = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200, db_index=True)
    address = models.TextField()
    hostel_type = models.CharField(max_length=50, choices=HOSTEL_TYPES)
    gender_allowed = models.CharField(max_length=20, choices=GENDER_CHOICES, default='mixed')
    
    # Contact Information
    warden_name = models.CharField(max_length=100)
    warden_phone = models.CharField(max_length=20)
    warden_email = models.EmailField(blank=True)
    
    # Pricing (Tanzania Shillings)
    price_per_semester = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    caution_money = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Facilities & Features
    AMENITIES_CHOICES = [
        ('wifi', 'High-Speed WiFi'),
        ('library', 'Study Library'),
        ('cafeteria', 'Cafeteria'),
        ('laundry', 'Laundry Service'),
        ('security', '24/7 Security'),
        ('cleaning', 'Daily Cleaning'),
        ('hot_water', 'Hot Water'),
        ('generator', 'Backup Generator'),
        ('parking', 'Secure Parking'),
        ('sports', 'Sports Facilities'),
        ('medical', 'Medical Room'),
        ('kitchen', 'Shared Kitchen'),
    ]
    
    amenities = models.JSONField(default=list, blank=True)
    total_rooms = models.IntegerField(default=1)
    available_rooms = models.IntegerField(default=1)
    total_capacity = models.IntegerField(default=1)
    current_occupancy = models.IntegerField(default=0)
    
    # Academic Information
    academic_year = models.CharField(max_length=20, default="2024/2025")
    semester = models.CharField(max_length=20, choices=[
        ('sem1', 'Semester 1'),
        ('sem2', 'Semester 2'),
        ('short', 'Short Course'),
    ])
    
    # Status
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Images
    main_image = models.ImageField(upload_to='hostels/main/', null=True, blank=True)
    image_1 = models.ImageField(upload_to='hostels/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='hostels/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='hostels/', null=True, blank=True)
    image_4 = models.ImageField(upload_to='hostels/', null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['university']),
            models.Index(fields=['price_per_semester']),
            models.Index(fields=['is_available']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.university}"
    
    def get_all_images(self):
        """Get all images for the hostel"""
        images = []
        if self.main_image:
            images.append(self.main_image.url)
        for field in [self.image_1, self.image_2, self.image_3, self.image_4]:
            if field:
                images.append(field.url)
        return images
    
    def get_occupancy_rate(self):
        """Calculate occupancy percentage"""
        if self.total_capacity > 0:
            return (self.current_occupancy / self.total_capacity) * 100
        return 0
    
    def get_short_description(self):
        """Get truncated description"""
        if len(self.description) > 150:
            return self.description[:150] + '...'
        return self.description

class HostelBooking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    PAYMENT_OPTIONS = [
        ('full_semester', 'Full Semester Payment'),
        ('monthly', 'Monthly Installments'),
        ('half_semester', 'Half Semester Payment'),
    ]
    
    # Student Information
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    student_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, help_text="University Registration Number")  # RENAME
    student_email = models.EmailField()
    student_phone = models.CharField(max_length=20)
    student_course = models.CharField(max_length=100)
    student_year = models.CharField(max_length=20, choices=[
        ('1', 'Year 1'), ('2', 'Year 2'), ('3', 'Year 3'), 
        ('4', 'Year 4'), ('5', 'Year 5'), ('diploma', 'Diploma')
    ])
    
    # Booking Details
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='bookings')
    booking_type = models.CharField(max_length=20, choices=[
        ('semester', 'Full Semester'),
        ('monthly', 'Monthly'),
        ('short_term', 'Short Term'),
        ('academic_year', 'Full Academic Year'),
    ])
    payment_option = models.CharField(max_length=20, choices=PAYMENT_OPTIONS, default='full_semester')
    
    # Academic Period
    academic_year = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    check_in_date = models.DateField()
    check_out_date = models.DateField(null=True, blank=True)
    duration_months = models.IntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(12)])
    
    # Payment Information
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_deadline = models.DateField()
    
    # Status
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    payment_status = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    
    # Guardian Information
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    guardian_relationship = models.CharField(max_length=50, blank=True)
    
    # Special Requirements
    special_needs = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)
    
    # Dates
    booking_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-booking_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['student_id']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-calculate total amount
        if not self.total_amount:
            if self.booking_type == 'semester':
                self.total_amount = self.hostel.price_per_semester + self.hostel.security_deposit + self.hostel.caution_money
            elif self.booking_type == 'monthly':
                self.total_amount = (self.hostel.price_per_month * self.duration_months) + self.hostel.security_deposit + self.hostel.caution_money
            else:  # academic year
                self.total_amount = (self.hostel.price_per_semester * 2) + self.hostel.security_deposit + self.hostel.caution_money
        
        # Auto-calculate balance
        self.balance = self.total_amount - self.amount_paid
        
        # Auto-set check-out date
        if not self.check_out_date:
            self.check_out_date = self.check_in_date + datetime.timedelta(days=30 * self.duration_months)
        
        # Auto-set payment deadline (2 weeks before check-in)
        if not self.payment_deadline:
            self.payment_deadline = self.check_in_date - datetime.timedelta(days=14)
        
        # Update hostel occupancy
        if self.status == 'confirmed' and not self._state.adding:
            self.hostel.current_occupancy += 1
            self.hostel.available_rooms = max(0, self.hostel.total_rooms - (self.hostel.current_occupancy // 4))
            self.hostel.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Booking #{self.id} - {self.student_name}"
    
    def calculate_total_amount(self):
        """Calculate total booking amount"""
        if self.booking_type == 'semester':
            return self.hostel.price_per_semester + self.hostel.security_deposit + self.hostel.caution_money
        elif self.booking_type == 'monthly':
            return (self.hostel.price_per_month * self.duration_months) + self.hostel.security_deposit + self.hostel.caution_money
        else:
            return (self.hostel.price_per_semester * 2) + self.hostel.security_deposit + self.hostel.caution_money

class HostelReview(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    student_name = models.CharField(max_length=100)
    student_course = models.CharField(max_length=100)
    student_year = models.CharField(max_length=20)
    
    # Ratings
    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    cleanliness = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    security = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    facilities = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    management = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    review_title = models.CharField(max_length=200)
    review_text = models.TextField()
    
    # Recommendations
    would_recommend = models.BooleanField(default=True)
    stay_duration = models.CharField(max_length=20, choices=[
        ('semester', 'One Semester'),
        ('year', 'One Year'),
        ('multiple', 'Multiple Years'),
        ('short', 'Short Stay'),
    ])
    
    # Status
    is_approved = models.BooleanField(default=False)
    is_verified_student = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['hostel']),
            models.Index(fields=['overall_rating']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"Review by {self.student_name} - {self.overall_rating} stars"
    
    def get_average_rating(self):
        """Calculate average of all ratings"""
        ratings = [self.overall_rating, self.cleanliness, self.security, self.facilities, self.management]
        return sum(ratings) / len(ratings)
