# guesthouse_booking/urls.py
from django.urls import path, include


urlpatterns = [
    path('', include('bookings.urls')),
]
