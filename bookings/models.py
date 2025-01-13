# bookings/models.py

from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Amenity(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название удобства")

    history = HistoricalRecords()  # Отслеживание истории

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Удобство"
        verbose_name_plural = "Удобства"


class Room(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название номера")
    room_number = models.CharField(max_length=10, verbose_name="Номер комнаты")
    room_type = models.CharField(max_length=50, verbose_name="Тип номера")
    price_per_night = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Цена за ночь")
    max_occupancy = models.IntegerField(verbose_name="Максимальная вместимость")
    amenities = models.ManyToManyField('Amenity', blank=True, verbose_name="Удобства")
    image = models.ImageField(upload_to='images/', verbose_name="Изображение")

    history = HistoricalRecords()  # Отслеживание истории

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Номер"
        verbose_name_plural = "Номера"
        ordering = ['name']


class Guest(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(verbose_name="Электронная почта")
    phone_number = models.CharField(max_length=20, verbose_name="Телефон")
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокирован")

    history = HistoricalRecords()  # Отслеживание истории

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Гость"
        verbose_name_plural = "Гости"
        ordering = ['last_name', 'first_name']


class Booking(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, verbose_name="Гость")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Номер")
    check_in = models.DateField(verbose_name="Дата заезда")
    check_out = models.DateField(verbose_name="Дата выезда")
    total_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Суммарная стоимость")
    booking_name = models.CharField(max_length=255, verbose_name="Название бронирования")
    is_paid = models.BooleanField(default=False, verbose_name="Оплачено")

    history = HistoricalRecords()  # Отслеживание истории

    def __str__(self):
        return f"{self.booking_name} ({self.guest.first_name} {self.guest.last_name})"

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['check_in']


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, verbose_name="Бронирование")
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Сумма платежа")
    payment_date = models.DateField(verbose_name="Дата платежа")

    history = HistoricalRecords()  # Отслеживание истории

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ['payment_date']


class Review(models.Model):
    guest_name = models.CharField(max_length=100, verbose_name="Имя гостя")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Номер")
    rating = models.IntegerField(verbose_name="Оценка")
    comment = models.TextField(verbose_name="Комментарий")
    review_date = models.DateField(default=timezone.now, verbose_name="Дата отзыва")

    history = HistoricalRecords()  # Отслеживание истории

    def __str__(self):
        return f"Обзор от пользователя {self.guest_name} для «{self.room.name}»"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['review_date']
