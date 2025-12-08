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

    @property
    def digits_price(self):
        """
        Rudisha digits tu (0-9) kutoka kwenye field price.
        Mfano: "Tsh 350,000 /=" -> "350000"
        """
        if not self.price:
            return ''
        try:
            return re.sub(r'[^0-9]', '', str(self.price))
        except Exception:
            # defensive: ili avoid crash kama price ni kitu kisichotarajiwa
            return ''
    
    class Meta:
        indexes = [
            models.Index(fields=['title', 'location', 'description']),
            models.Index(fields=['property_type']),
            models.Index(fields=['bedrooms']),
            models.Index(fields=['price']),
            models.Index(fields=['is_featured']),
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