from django.utils import timezone
from rest_framework import serializers

from .models import Amenity, Room, Guest, Booking, Payment, Review


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name']


class RoomSerializer(serializers.ModelSerializer):
    amenities = AmenitySerializer(many=True, read_only=True)
    name = serializers.CharField(required=True, help_text="Название комнаты")

    class Meta:
        model = Room
        fields = ['id', 'name', 'room_number', 'room_type', 'price_per_night', 'max_occupancy', 'amenities', 'image']

    def validate_price_per_night(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена за ночь должна быть положительным числом.")
        return value

    def validate_max_occupancy(self, value):
        if value <= 0:
            raise serializers.ValidationError("Максимальная вместимость должна быть положительным числом.")
        return value


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'is_blocked']

    def validate_email(self, value):
        if "@" not in value:
            raise serializers.ValidationError("Введите корректный адрес электронной почты.")
        return value

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Номер телефона должен содержать только цифры.")
        if len(value) < 10:
            raise serializers.ValidationError("Номер телефона должен содержать не менее 10 символов.")
        return value


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'guest', 'room', 'check_in', 'check_out', 'total_price', 'booking_name', 'is_paid']

    def validate(self, data):
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        if check_in and check_out and check_in >= check_out:
            raise serializers.ValidationError("Дата выезда должна быть позже даты заезда.")
        if check_in and check_in < timezone.now().date():
            raise serializers.ValidationError("Дата заезда не может быть в прошлом.")
        return data


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_date']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма платежа должна быть положительным числом.")
        return value

    def validate_payment_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Дата платежа не может быть в будущем.")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'guest_name', 'room', 'rating', 'comment', 'review_date']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Оценка должна быть в диапазоне от 1 до 5.")
        return value

    def validate_review_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Дата отзыва не может быть в будущем.")
        return value
