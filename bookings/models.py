# bookings/models.py

from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Amenity(models.Model):
    name = models.CharField(max_length=100)

    history = HistoricalRecords()  # Отслеживание истории

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=100)
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50)
    price_per_night = models.DecimalField(max_digits=6, decimal_places=2)
    max_occupancy = models.IntegerField()
    amenities = models.ManyToManyField('Amenity', blank=True)
    image = models.ImageField(upload_to='images/')

    history = HistoricalRecords()  # Отслеживание истории

    def __str__(self):
        return self.name


class Guest(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    is_blocked = models.BooleanField(default=False)
    history = HistoricalRecords()  # Отслеживание истории

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Booking(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Суммарная стоимость")
    booking_name = models.CharField(max_length=255)
    is_paid = models.BooleanField(default=False)

    history = HistoricalRecords()  # Отслеживание истории

    def __str__(self):
        return f"{self.booking_name} ({self.guest.first_name} {self.guest.last_name})"


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date = models.DateField()

    history = HistoricalRecords()  # Отслеживание истории


class Review(models.Model):
    guest_name = models.CharField(max_length=100)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    review_date = models.DateField(default=timezone.now)

    history = HistoricalRecords()  # Отслеживание истории

    def __str__(self):
        return f"Обзор от пользователя {self.guest_name} для «{self.room.name}»"
