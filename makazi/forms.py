# makazi/forms.py
from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Jina lako kamili'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Barua pepe yako'
        })
    )
    
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Namba ya simu'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Ujumbe wako...'
        })
    )
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']





# makazi/forms.py - Ongeza baada ya ContactForm
from django import forms
from .models import Apartment, ApartmentBooking, ApartmentReview
from django.core.validators import MinValueValidator
from django.utils import timezone

class ApartmentFilterForm(forms.Form):
    APARTMENT_TYPE_CHOICES = [
        ('', 'Any Type'),
        ('studio', 'Studio'),
        ('1bed', '1 Bedroom'),
        ('2bed', '2 Bedrooms'),
        ('3bed', '3 Bedrooms'),
        ('penthouse', 'Penthouse'),
        ('duplex', 'Duplex'),
    ]
    
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Enter location...',
        'class': 'form-control'
    }))
    
    apartment_type = forms.ChoiceField(
        choices=APARTMENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_price = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Min Price',
            'class': 'form-control'
        })
    )
    
    max_price = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Max Price',
            'class': 'form-control'
        })
    )
    
    bedrooms = forms.ChoiceField(
        choices=[
            ('', 'Any'),
            ('1', '1 Bedroom'),
            ('2', '2 Bedrooms'),
            ('3', '3 Bedrooms'),
            ('4', '4+ Bedrooms'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    amenities = forms.MultipleChoiceField(
        choices=[
            ('wifi', 'Wi-Fi'),
            ('parking', 'Parking'),
            ('pool', 'Swimming Pool'),
            ('gym', 'Gym'),
            ('security', '24/7 Security'),
            ('ac', 'Air Conditioning'),
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Amenities'
    )

class ApartmentBookingForm(forms.ModelForm):
    class Meta:
        model = ApartmentBooking
        fields = [
            'customer_name',
            'customer_email',
            'customer_phone',
            'check_in_date',
            'duration_months',
            'number_of_guests',
            'special_requests'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'check_in_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat()
            }),
            'duration_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 24,
                'placeholder': 'Number of months'
            }),
            'number_of_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requests or questions...'
            }),
        }
    
    def clean_check_in_date(self):
        check_in_date = self.cleaned_data.get('check_in_date')
        if check_in_date and check_in_date < timezone.now().date():
            raise forms.ValidationError("Check-in date cannot be in the past.")
        return check_in_date

class ApartmentReviewForm(forms.ModelForm):
    class Meta:
        model = ApartmentReview
        fields = ['reviewer_name', 'reviewer_email', 'rating', 'title', 'comment']
        widgets = {
            'reviewer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name'
            }),
            'reviewer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email (optional)'
            }),
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)], attrs={
                'class': 'form-select'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience...'
            }),
        }