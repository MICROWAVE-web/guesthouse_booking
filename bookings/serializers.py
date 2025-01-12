# bookings/serializers.py

from rest_framework import serializers

from .models import Amenity, Room, Guest, Booking, Payment, Review


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name']


class RoomSerializer(serializers.ModelSerializer):
    amenities = AmenitySerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'room_number', 'room_type', 'price_per_night', 'max_occupancy', 'amenities', 'image']


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number']


class BookingSerializer(serializers.ModelSerializer):
    guest = GuestSerializer(read_only=True)
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'guest', 'room', 'check_in', 'check_out', 'total_price', 'booking_name']


class PaymentSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_date']


class ReviewSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'guest_name', 'room', 'rating', 'comment', 'review_date']
