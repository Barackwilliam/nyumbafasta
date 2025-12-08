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