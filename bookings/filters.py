import django_filters

from .models import Room, Amenity, Review


class RoomFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Название номера')
    room_type = django_filters.CharFilter(lookup_expr='icontains', label='Тип номера')
    price_per_night = django_filters.NumberFilter(label='Цена за ночь')
    price_per_night__gte = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='gte',
                                                       label='Цена за ночь (от)')
    price_per_night__lte = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='lte',
                                                       label='Цена за ночь (до)')
    max_occupancy = django_filters.NumberFilter(label='Максимальная вместимость')
    max_occupancy__gte = django_filters.NumberFilter(field_name='max_occupancy', lookup_expr='gte',
                                                     label='Максимальная вместимость (от)')
    max_occupancy__lte = django_filters.NumberFilter(field_name='max_occupancy', lookup_expr='lte',
                                                     label='Максимальная вместимость (до)')
    amenities = django_filters.ModelMultipleChoiceFilter(
        field_name='amenities__name',
        queryset=Amenity.objects.all(),
        label='Удобства',
        conjoined=True,  # Искать номера, которые содержат ВСЕ выбранные удобства
    )

    class Meta:
        model = Room
        fields = ['name', 'room_type', 'max_occupancy', 'amenities']


class ReviewFilter(django_filters.FilterSet):
    guest_name = django_filters.CharFilter(lookup_expr='icontains', label='Имя гостя')
    room = django_filters.ModelChoiceFilter(queryset=Room.objects.all(), label='Номер')
    rating = django_filters.NumberFilter(label='Оценка')
    rating__gte = django_filters.NumberFilter(field_name='rating', lookup_expr='gte', label='Оценка (от)')
    rating__lte = django_filters.NumberFilter(field_name='rating', lookup_expr='lte', label='Оценка (до)')

    class Meta:
        model = Review
        fields = ['guest_name', 'room', 'rating']
