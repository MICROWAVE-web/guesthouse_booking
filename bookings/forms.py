from django import forms

from .models import Booking
from .models import Review
from .models import Room


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['guest_name', 'room', 'rating', 'comment', 'review_date']
        widgets = {
            'review_date': forms.DateInput(attrs={'type': 'date'}),
        }


class BookingForm(forms.ModelForm):
    room_id = forms.IntegerField(widget=forms.HiddenInput())
    room_name = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Booking
        fields = ['guest', 'room_id', 'room_name', 'check_in', 'check_out', 'total_price', 'is_paid']


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'room_number', 'room_type', 'price_per_night', 'max_occupancy', 'image', 'amenities']
