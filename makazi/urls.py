# makazi/urls.py
from django.urls import path
from . import views
from .views import apartments_list, apartment_detail, my_bookings, apartment_search


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



    path('apartments/', apartments_list, name='apartments_list'),
    path('apartments/<int:pk>/', apartment_detail, name='apartment_detail'),
    path('my-bookings/', my_bookings, name='my_bookings'),
    path('apartments/search/', apartment_search, name='apartment_search'),
    
]