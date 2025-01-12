# bookings/filters.py
import django_filters
from django.db.models import Q

from .models import Room


class RoomFilter(django_filters.FilterSet):
    amenities = django_filters.CharFilter(method='filter_amenities', label='Включая удобство (Напр. Wifi)')
    exclude_amenity = django_filters.CharFilter(method='filter_exclude_amenity', label='Исключить удобства')
    price_range = django_filters.NumericRangeFilter(field_name='price_per_night', label='Диапазон цен')
    max_occupancy = django_filters.NumberFilter(field_name='max_occupancy', lookup_expr='lte',
                                                label='Максимально человек')
    room_type = django_filters.CharFilter(field_name='room_type', lookup_expr='icontains', label='Тип комнаты')
    has_image = django_filters.BooleanFilter(method='filter_has_image', label='Наличие изображения')

    class Meta:
        model = Room
        fields = ['amenities', 'price_range', 'max_occupancy', 'room_type', 'has_image']

    def filter_amenities(self, queryset, name, value):
        """
        Фильтрует комнаты, которые имеют указанные удобства (OR-условие).
        Пример: ?amenities=WiFi,балкон
        """
        amenities = value.split(',')  # Пример: WiFi,балкон
        query = Q()
        for amenity in amenities:
            query |= Q(amenities__name__icontains=amenity)
        return queryset.filter(query).distinct()

    def filter_exclude_amenity(self, queryset, name, value):
        """
        Исключает комнаты с указанным удобством (NOT-условие).
        Пример: ?exclude_amenity=WiFi
        """
        return queryset.exclude(amenities__name__icontains=value)

    def filter_has_image(self, queryset, name, value):
        """
        Фильтрует комнаты в зависимости от наличия изображения.
        Пример: ?has_image=True
        """
        if value:
            return queryset.exclude(image='')
        return queryset.filter(image='')
