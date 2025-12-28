# makazi/admin.py
from django.contrib import admin
from .models import Scrape_MakaziListing, ContactMessage

@admin.register(Scrape_MakaziListing)
class MakaziListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'property_type', 'bedrooms', 'is_featured', 'is_verified', 'scraped_at')
    list_filter = ('location', 'property_type', 'is_featured', 'is_verified', 'scraped_at')
    search_fields = ('title', 'location', 'description')
    list_editable = ('is_featured', 'is_verified')
    list_per_page = 50

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'listing', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    list_editable = ('is_read',)


# # makazi/admin.py
# from django.contrib import admin
# from .models import Apartment, ApartmentBooking, ApartmentReview

# @admin.register(Apartment)
# class ApartmentAdmin(admin.ModelAdmin):
#     list_display = ['title', 'location', 'price_per_month', 'is_available', 'is_featured', 'created_at']
#     list_filter = ['is_available', 'is_featured', 'is_verified', 'apartment_type', 'location']
#     search_fields = ['title', 'location', 'description', 'owner_name']
#     readonly_fields = ['created_at', 'updated_at']
#     fieldsets = (
#         ('Basic Information', {
#             'fields': ('title', 'description', 'location', 'address')
#         }),
#         ('Apartment Details', {
#             'fields': ('apartment_type', 'price_per_month', 'security_deposit', 'maintenance_fee')
#         }),
#         ('Specifications', {
#             'fields': ('total_rooms', 'bedrooms', 'bathrooms', 'area_sqft', 'floor_number', 'total_floors')
#         }),
#         ('Amenities', {
#             'fields': ('amenities',)
#         }),
#         ('Images', {
#             'fields': ('main_image', 'image_1', 'image_2', 'image_3', 'image_4')
#         }),
#         ('Contact Information', {
#             'fields': ('owner_name', 'owner_phone', 'owner_email')
#         }),
#         ('Status', {
#             'fields': ('is_available', 'is_featured', 'is_verified')
#         }),
#         ('Location', {
#             'fields': ('latitude', 'longitude')
#         }),
#         ('Dates', {
#             'fields': ('created_at', 'updated_at')
#         }),
#     )
    
#     def get_readonly_fields(self, request, obj=None):
#         if obj:  # editing an existing object
#             return self.readonly_fields + ('created_at', 'updated_at')
#         return self.readonly_fields

# @admin.register(ApartmentBooking)
# class ApartmentBookingAdmin(admin.ModelAdmin):
#     list_display = ['id', 'apartment', 'customer_name', 'check_in_date', 'duration_months', 'status', 'payment_status', 'booking_date']
#     list_filter = ['status', 'payment_status', 'booking_date']
#     search_fields = ['customer_name', 'customer_email', 'customer_phone', 'apartment__title']
#     readonly_fields = ['booking_date', 'confirmation_date', 'cancellation_date', 'total_amount']
#     actions = ['confirm_bookings', 'cancel_bookings']
    
#     def confirm_bookings(self, request, queryset):
#         updated = queryset.update(status='confirmed')
#         self.message_user(request, f'{updated} booking(s) confirmed successfully.')
#     confirm_bookings.short_description = "Confirm selected bookings"
    
#     def cancel_bookings(self, request, queryset):
#         updated = queryset.update(status='cancelled')
#         self.message_user(request, f'{updated} booking(s) cancelled successfully.')
#     cancel_bookings.short_description = "Cancel selected bookings"

# @admin.register(ApartmentReview)
# class ApartmentReviewAdmin(admin.ModelAdmin):
#     list_display = ['reviewer_name', 'apartment', 'rating', 'is_approved', 'created_at']
#     list_filter = ['rating', 'is_approved', 'created_at']
#     search_fields = ['reviewer_name', 'apartment__title', 'title', 'comment']
#     actions = ['approve_reviews', 'disapprove_reviews']
    
#     def approve_reviews(self, request, queryset):
#         updated = queryset.update(is_approved=True)
#         self.message_user(request, f'{updated} review(s) approved successfully.')
#     approve_reviews.short_description = "Approve selected reviews"
    
#     def disapprove_reviews(self, request, queryset):
#         updated = queryset.update(is_approved=False)
#         self.message_user(request, f'{updated} review(s) disapproved successfully.')
#     disapprove_reviews.short_description = "Disapprove selected reviews"






# makazi/admin.py
from django.contrib import admin
from django import forms
from .models import Apartment, ApartmentBooking, ApartmentReview

class ApartmentAdminForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: Customize the form if needed

@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    form = ApartmentAdminForm
    list_display = ['title', 'location', 'price_per_month', 'is_available', 'is_featured', 'created_at']
    list_filter = ['is_available', 'is_featured', 'is_verified', 'apartment_type', 'location']
    search_fields = ['title', 'location', 'description', 'owner_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'location', 'address')
        }),
        ('Apartment Details', {
            'fields': ('apartment_type', 'price_per_month', 'security_deposit', 'maintenance_fee')
        }),
        ('Specifications', {
            'fields': ('total_rooms', 'bedrooms', 'bathrooms', 'area_sqft', 'floor_number', 'total_floors')
        }),
        ('Amenities', {
            'fields': ('amenities',)
        }),
        ('Images', {
            'fields': ('main_image', 'image_1', 'image_2', 'image_3', 'image_4')
        }),
        ('Contact Information', {
            'fields': ('owner_name', 'owner_phone', 'owner_email')
        }),
        ('Status', {
            'fields': ('is_available', 'is_featured', 'is_verified')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            # Convert tuple to list and add new fields
            readonly_fields = list(self.readonly_fields)
            readonly_fields.append('created_at')
            readonly_fields.append('updated_at')
            return readonly_fields
        return self.readonly_fields

@admin.register(ApartmentBooking)
class ApartmentBookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'apartment', 'customer_name', 'check_in_date', 'duration_months', 'status', 'payment_status', 'booking_date']
    list_filter = ['status', 'payment_status', 'booking_date']
    search_fields = ['customer_name', 'customer_email', 'customer_phone', 'apartment__title']
    readonly_fields = ['booking_date', 'confirmation_date', 'cancellation_date', 'total_amount']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('apartment', 'customer_name', 'customer_email', 'customer_phone')
        }),
        ('Booking Details', {
            'fields': ('check_in_date', 'check_out_date', 'duration_months', 'number_of_guests')
        }),
        ('Payment Information', {
            'fields': ('total_amount', 'security_deposit_paid', 'maintenance_fee_paid', 'monthly_rent', 'payment_status')
        }),
        ('Status', {
            'fields': ('status', 'special_requests')
        }),
        ('Dates', {
            'fields': ('booking_date', 'confirmation_date', 'cancellation_date')
        }),
    )
    
    actions = ['confirm_bookings', 'cancel_bookings']
    
    def confirm_bookings(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} booking(s) confirmed successfully.')
    confirm_bookings.short_description = "Confirm selected bookings"
    
    def cancel_bookings(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} booking(s) cancelled successfully.')
    cancel_bookings.short_description = "Cancel selected bookings"

@admin.register(ApartmentReview)
class ApartmentReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer_name', 'apartment', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['reviewer_name', 'apartment__title', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('apartment', 'reviewer_name', 'reviewer_email')
        }),
        ('Review Details', {
            'fields': ('rating', 'title', 'comment')
        }),
        ('Status', {
            'fields': ('is_approved',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} review(s) approved successfully.')
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} review(s) disapproved successfully.')
    disapprove_reviews.short_description = "Disapprove selected reviews"