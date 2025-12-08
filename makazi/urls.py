# makazi/urls.py
from django.urls import path
from . import views

app_name = 'makazi'

urlpatterns = [
    path('', views.home, name='home'),
    path('listings/', views.property_listings, name='listings'),
    path('listing/<slug:slug_id>/', views.property_detail, name='property_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('contact/<int:listing_id>/', views.contact_about_listing, name='contact_about_listing'),
    path('api/filter/', views.filter_properties_api, name='filter_api'),
    path('api/search/', views.search_properties_api, name='search_api'),
    path('dashboard/', views.dashboard, name='dashboard'),
]