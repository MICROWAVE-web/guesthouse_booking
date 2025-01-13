# bookings/filters.py
import django_filters
from django.db.models import Q

from .models import Room, Booking


class BookingFilter(django_filters.FilterSet):
    """
    Фильтр для модели Booking.
    """
    check_in_after = django_filters.DateFilter(field_name="check_in", lookup_expr="gte", label="Check-in After")
    check_out_before = django_filters.DateFilter(field_name="check_out", lookup_expr="lte", label="Check-out Before")
    min_total_price = django_filters.NumberFilter(field_name="total_price", lookup_expr="gte", label="Min Total Price")
    max_total_price = django_filters.NumberFilter(field_name="total_price", lookup_expr="lte", label="Max Total Price")
    is_paid = django_filters.BooleanFilter(field_name="is_paid", label="Is Paid")

    class Meta:
        model = Booking
        fields = ['check_in_after', 'check_out_before', 'min_total_price', 'max_total_price', 'is_paid', 'guest']
