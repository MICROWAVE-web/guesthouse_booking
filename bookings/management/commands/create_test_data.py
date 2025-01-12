import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Amenity, Room, Guest, Booking, Payment, Review


class Command(BaseCommand):
    help = 'Создаем тестовые данные для моделей Amenity, Room, Guest, Booking, Payment, Review моделей'

    def handle(self, *args, **kwargs):
        self.stdout.write("Создание тестовых данных...")

        # Создание 10 Amenity
        for i in range(1, 11):
            Amenity.objects.create(name=f"Удобство {i}")
        self.stdout.write(self.style.SUCCESS('Удобства созданы'))

        # Создание 10 Room
        amenities = list(Amenity.objects.all())
        for i in range(1, 11):
            room = Room.objects.create(
                name=f"Комната {i}",
                room_number=f"10{i}",
                room_type=random.choice(["Standard", "Deluxe", "Suite"]),
                price_per_night=random.uniform(50, 200),
                max_occupancy=random.randint(1, 4),
                image=f"images/room_{i}.jpg"
            )
            room.amenities.set(random.sample(amenities, k=random.randint(1, 5)))
        self.stdout.write(self.style.SUCCESS('Комнаты созданы'))

        # Создание 10 Guest
        for i in range(1, 11):
            Guest.objects.create(
                first_name=f"Имя_{i}",
                last_name=f"Фамилия_{i}",
                email=f"guest{i}@example.com",
                phone_number=f"+7900123456{i}"
            )
        self.stdout.write(self.style.SUCCESS('Гости созданы'))

        # Создание 10 Booking
        guests = list(Guest.objects.all())
        rooms = list(Room.objects.all())
        for i in range(1, 11):
            check_in = timezone.now().date() + timezone.timedelta(days=random.randint(1, 30))
            check_out = check_in + timezone.timedelta(days=random.randint(1, 10))
            Booking.objects.create(
                guest=random.choice(guests),
                room=random.choice(rooms),
                check_in=check_in,
                check_out=check_out,
                total_price=random.uniform(100, 1000),
                booking_name=f"Бронирование {i}"
            )
        self.stdout.write(self.style.SUCCESS('Бронирования созданы'))

        # Создание 10 Payment
        bookings = list(Booking.objects.all())
        for i in range(1, 11):
            Payment.objects.create(
                booking=random.choice(bookings),
                amount=random.uniform(50, 500),
                payment_date=timezone.now().date()
            )
        self.stdout.write(self.style.SUCCESS('Платежи созданы'))

        # Создание 10 Review
        for i in range(1, 11):
            Review.objects.create(
                guest_name=f"Гость_{i}",
                room=random.choice(rooms),
                rating=random.randint(1, 5),
                comment=f"Отличный сервис! {i}",
                review_date=timezone.now().date()
            )
        self.stdout.write(self.style.SUCCESS('Отзывы созданы'))

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!'))
