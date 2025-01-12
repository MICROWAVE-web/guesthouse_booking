# bookings/api_views.py
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import RoomFilter
from .models import Amenity, Room, Guest, Booking, Payment, Review
from .serializers import (
    AmenitySerializer,
    RoomSerializer,
    GuestSerializer,
    BookingSerializer,
    PaymentSerializer,
    ReviewSerializer,
)


class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all().order_by('price_per_night')  # Упорядочим по цене за ночь
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RoomFilter

    @action(methods=['GET'], detail=False)
    def is_valid_to_book(self, request):
        """
        Фильтрация комнаты на предмет возможности аренды в заданном промежутке времени
        Напр. /api/rooms/is_valid_to_book?room_name=Deluxe&date_range=2024-01-01,2024-01-10
        """
        room_name = request.query_params.get('room_name', None)
        date_range = request.query_params.get('date_range', None)

        query = Q()
        room_exist_query = Q()
        if room_name and date_range:
            room_exist_query &= Q(room__name__icontains=room_name)
            query &= Q(room__name__icontains=room_name)
            start_date, end_date = date_range.split(',')
            query &= Q(check_in__gte=start_date) & Q(check_out__lte=end_date)
        else:
            return Response({"message": f"Not enough conditions."}, status=200)

        # Проверка на то что комната существует
        if not Booking.objects.filter(room_exist_query).exists():
            return Response({"message": f"Room '{room_name}' not found."}, status=200)

        if Booking.objects.filter(query).exists():
            # Заказы на эту комнату в этот промежуток времени уже есть.
            return Response({"message": f"This room is already booked."}, status=200)
        else:
            # Заказы на эту комнату в этот промежуток времени нет, комнату можно заказать.
            return Response({"message": f"This room is ready to book."}, status=200)


class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
