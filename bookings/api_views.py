# bookings/api_views.py
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

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
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']

    def get_queryset(self):
        """
        queryset с использованием Q-выражений для фильтрации удобств.
        """
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
            )

        return queryset

    @action(methods=['GET'], detail=False)
    def popular_amenities(self, request):
        """
        Кастомный endpoint для получения популярных удобств (пример: используется в более чем 5 комнатах).
        """
        from django.db.models import Count
        popular_amenities = Amenity.objects.annotate(room_count=Count('room')).filter(room_count__gte=5)
        serializer = self.get_serializer(popular_amenities, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def mark_as_popular(self, request, pk=None):
        """
        Отметить удобство как популярное.
        Пример: /api/amenities/1/mark_as_popular/
        """
        amenity = self.get_object()
        amenity.name += ' (Выбирают чаще всего!)'
        amenity.save()
        return Response({'message': f'Удобство "{amenity.name}" отмечено как популярное!'})


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all().order_by('price_per_night')  # Упорядочим по цене за ночь
    serializer_class = RoomSerializer

    @action(methods=['GET'], detail=False)
    def is_valid_to_book(self, request):
        """
        Фильтрация комнаты на предмет возможности аренды в заданном промежутке времени
        Пример: /api/rooms/is_valid_to_book?room_name=Deluxe&date_range=2024-01-01,2024-01-10
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

    @action(methods=['GET'], detail=False)
    def filter_rooms(self, request):
        """
        Фильтрация комнат по различным параметрам.
        Пример: /api/rooms/filter_rooms/?amenities=удобство&price_min=50&price_max=500&max_occupancy=1&room_type=Suite&has_image=True
        """
        queryset = self.get_queryset()
        query = Q()

        # Фильтрация по удобствам (OR-условие)
        amenities = request.query_params.get('amenities', None)
        if amenities:
            amenities_list = amenities.split(',')
            for amenity in amenities_list:
                query |= Q(amenities__name__iregex=amenity)

        # Исключение комнат с указанным удобством
        exclude_amenity = request.query_params.get('exclude_amenity', None)
        if exclude_amenity:
            query &= ~Q(amenities__name__iregex=exclude_amenity)

        # Фильтрация по минимальной цене
        price_min = request.query_params.get('price_min', None)
        if price_min:
            query &= Q(price_per_night__gte=float(price_min))

        # Фильтрация по максимальной цене
        price_max = request.query_params.get('price_max', None)
        if price_max:
            query &= Q(price_per_night__lte=float(price_max))

        # Фильтрация по максимальной вместимости
        max_occupancy = request.query_params.get('max_occupancy', None)
        if max_occupancy:
            query &= Q(max_occupancy__lte=int(max_occupancy))

        # Фильтрация по типу комнаты
        room_type = request.query_params.get('room_type', None)
        if room_type:
            query &= Q(room_type__icontains=room_type)

        queryset = queryset.filter(query).distinct()

        # Фильтрация по наличию изображения
        has_image = request.query_params.get('has_image', None)
        if has_image:
            has_image = has_image.lower() == 'true'
            if has_image:

                queryset = queryset.exclude(image='')
            else:
                queryset = queryset.filter(image='')

        # Сериализация и возврат результата
        queryset = queryset.filter(query).distinct()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def mark_as_popular(self, request, pk=None):
        """
        Отметить комнату как популярное.
        Пример: /api/rooms/1/mark_as_popular/
        """
        room = self.get_object()
        room.name += ' (Выбирают чаще всего!)'
        room.save()
        return Response({'message': f'Комната "{room.name}" отмечена как популярная!'})


class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']

    def get_queryset(self):
        """
        Доработка queryset с использованием Q-выражений.
        Например, поиск по имени, фамилии или email.
        """
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone_number__icontains=search)
            )
        return queryset

    @action(methods=['GET'], detail=False)
    def recent_guests(self, request):
        """
        Кастомный endpoint для получения последних 5 гостей.
        """
        recent_guests = Guest.objects.all().order_by('-id')[:5]
        serializer = self.get_serializer(recent_guests, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def block_guest(self, request, pk=None):
        """
        Заблокировать гостя.
        Пример: /api/guests/1/block_guest/
        """
        guest = self.get_object()
        guest.is_blocked = True
        guest.save()
        return Response({'message': f'Гость "{guest.first_name} {guest.last_name}" заблокирован.'})


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['booking_name', 'guest__first_name', 'guest__last_name', 'room__room_number']
    ordering_fields = ['check_in', 'check_out', 'total_price']

    def get_queryset(self):
        """
        Доработка queryset с использованием Q-выражений для поиска.
        """
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        check_in_after = self.request.query_params.get('check_in_after')
        check_out_before = self.request.query_params.get('check_out_before')

        if search:
            queryset = queryset.filter(
                Q(guest__first_name__icontains=search) |
                Q(guest__last_name__icontains=search) |
                Q(booking_name__icontains=search) |
                Q(room__room_number__icontains=search)
            )

        if check_in_after:
            queryset = queryset.filter(check_in__gte=check_in_after)

        if check_out_before:
            queryset = queryset.filter(check_out__lte=check_out_before)

        return queryset

    @action(methods=['GET'], detail=False)
    def filter_bookings(self, request):
        """
        Фильтрация бронирований по различным параметрам.
        Пример: /api/bookings/filter_bookings/?check_in_after=2024-01-01&check_out_before=2025-02-10&min_total_price=70&max_total_price=500&is_paid=False
        """
        queryset = self.get_queryset()
        query = Q()
        # Фильтрация по дате заезда (check-in after)
        check_in_after = request.query_params.get('check_in_after', None)
        if check_in_after:
            query &= Q(check_in__gte=check_in_after)

        # Фильтрация по дате выезда (check-out before)
        check_out_before = request.query_params.get('check_out_before', None)
        if check_out_before:
            query &= Q(check_out__lte=check_out_before)

        # Фильтрация по минимальной общей цене
        min_total_price = request.query_params.get('min_total_price', None)
        if min_total_price:
            query &= Q(total_price__gte=float(min_total_price))

        # Фильтрация по максимальной общей цене
        max_total_price = request.query_params.get('max_total_price', None)
        if max_total_price:
            query &= Q(total_price__lte=float(max_total_price))

        # Фильтрация по статусу оплаты
        is_paid = request.query_params.get('is_paid', None)
        if is_paid:
            is_paid = is_paid.lower() == 'false'
            # queryset = queryset.filter(is_paid=is_paid)
            query &= ~Q(is_paid=is_paid)

        # Фильтрация по гостю
        guest = request.query_params.get('guest', None)
        if guest:
            # queryset = queryset.filter(guest__id=guest)
            query &= Q(guest__id=guest)

        # Применяем фильтры к queryset
        queryset = queryset.filter(query)

        # Сериализация и возврат результата
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def active_bookings(self, request):
        """
        Кастомный endpoint для получения активных бронирований.
        """
        active_bookings = Booking.objects.filter(
            Q(check_in__lte=timezone.now().date()) &
            Q(check_out__gte=timezone.now().date())
        )
        serializer = self.get_serializer(active_bookings, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def mark_as_paid(self, request, pk=None):
        """
        Отметить бронирование как оплаченное.
        Пример: /api/bookings/1/mark_as_paid/
        """
        booking = self.get_object()
        booking.is_paid = True
        booking.save()
        return Response({'message': f'Бронь "{booking.booking_name}" оплачена.'})


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['booking__guest__first_name', 'booking__guest__last_name', 'booking__booking_name']
    ordering_fields = ['amount', 'payment_date']

    def get_queryset(self):
        """
        Доработка queryset с использованием Q-выражений для фильтрации платежей.
        """
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        payment_date = self.request.query_params.get('payment_date')

        if search:
            queryset = queryset.filter(
                Q(booking__guest__first_name__icontains=search) |
                Q(booking__guest__last_name__icontains=search) |
                Q(booking__booking_name__icontains=search)
            )

        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)

        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)

        if payment_date:
            queryset = queryset.filter(payment_date=payment_date)

        return queryset

    @action(methods=['GET'], detail=False)
    def recent_payments(self, request):
        """
        Кастомный endpoint для получения последних 5 платежей.
        """
        recent_payments = Payment.objects.all().order_by('-payment_date')[:5]
        serializer = self.get_serializer(recent_payments, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['guest_name', 'room__name', 'comment']
    ordering_fields = ['rating', 'review_date']

    def get_queryset(self):
        """
        Доработка queryset с использованием Q-выражений для фильтрации отзывов.
        """
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        min_rating = self.request.query_params.get('min_rating')
        max_rating = self.request.query_params.get('max_rating')
        review_date = self.request.query_params.get('review_date')

        if search:
            queryset = queryset.filter(
                Q(guest_name__icontains=search) |
                Q(room__name__icontains=search) |
                Q(comment__icontains=search)
            )

        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)

        if max_rating:
            queryset = queryset.filter(rating__lte=max_rating)

        if review_date:
            queryset = queryset.filter(review_date=review_date)

        return queryset

    @action(methods=['GET'], detail=False)
    def top_reviews(self, request):
        """
        Кастомный endpoint для получения отзывов с самым высоким рейтингом.
        """
        top_reviews = Review.objects.filter(rating=5).order_by('-review_date')[:10]
        serializer = self.get_serializer(top_reviews, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def custom_action(self, request, pk=None):
        """
        Кастомное действие для обработки POST-запроса к конкретному отзыву.
        """
        review = self.get_object()
        return Response({'message': f'Custom action performed on Review for {review.room.name}.'})
