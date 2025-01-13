# bookings/admin.py


from django.contrib import admin
from django.db.models import Q
from django.utils import timezone
from import_export.admin import ExportActionMixin
from simple_history.admin import SimpleHistoryAdmin

from .models import Guest, Room, Booking, Payment, Review, Amenity
from .resources import BookingResource


class AmenityInline(admin.TabularInline):
    model = Room.amenities.through
    extra = 1


@admin.register(Guest)
class GuestAdmin(SimpleHistoryAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')
    list_display_links = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('first_name', 'last_name')
    fieldsets = (
        ("Персональная информация", {"fields": ("first_name", "last_name")}),
        ("Контактная информация", {"fields": ("email", "phone_number")}),
    )


@admin.register(Room)
class RoomAdmin(SimpleHistoryAdmin):
    list_display = (
        'name', 'room_number', 'room_type', 'price_per_night', 'max_occupancy', 'image', 'display_amenities')
    list_filter = ('room_type',)
    search_fields = ('room_number', 'room_type')
    inlines = [AmenityInline]

    @admin.display(description='Amenities')
    def display_amenities(self, obj):
        return ", ".join([amenity.name for amenity in obj.amenities.all()])


@admin.register(Booking)
class BookingAdmin(ExportActionMixin, SimpleHistoryAdmin):
    resource_class = BookingResource  # Для экспорта в excel
    list_display = ('booking_name', 'guest', 'room', 'check_in', 'check_out', 'total_price')
    list_display_links = ('guest', 'room')  # Гиперссылки на связанные записи
    list_filter = ('check_in', 'check_out')
    date_hierarchy = 'check_in'
    raw_id_fields = ('guest', 'room')
    search_fields = ('guest__first_name', 'guest__last_name', 'room__room_number')

    def get_export_queryset(self, request):
        """
        Кастомизация queryset для экспорта.
        Экспортирует только активные бронирования (текущие или будущие).
        """
        current_date = timezone.now().date()  # Текущая дата
        return Booking.objects.filter(
            Q(check_out__gte=current_date)  # Бронирования, которые ещё активны или будут активны
        ).order_by('check_in')  # Сортируем


@admin.register(Payment)
class PaymentAdmin(SimpleHistoryAdmin):
    list_display = ('booking', 'amount', 'payment_date', 'guest_name', 'room_number')
    list_filter = ('payment_date', 'booking__room__room_type')  # Фильтр по типу комнаты
    date_hierarchy = 'payment_date'
    search_fields = ('booking__guest__first_name', 'booking__guest__last_name', 'booking__room__room_number')
    fieldsets = (
        (None, {'fields': ('booking', 'amount', 'payment_date')}),
        ('Дополнительно', {'fields': ('guest_name', 'room_number'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('guest_name', 'room_number')  # Дополнительные вычисляемые поля

    @admin.display(description='Гость')
    def guest_name(self, obj):
        return f"{obj.booking.guest.first_name} {obj.booking.guest.last_name}"

    @admin.display(description='Номер комнаты')
    def room_number(self, obj):
        return obj.booking.room.room_number


@admin.register(Review)
class ReviewAdmin(SimpleHistoryAdmin):
    list_display = ('guest_name', 'room', 'rating', 'comment_preview', 'review_date')
    list_filter = ('rating', 'review_date', 'room__room_type')  # Фильтр по типу комнаты
    search_fields = ('guest_name', 'room__name', 'room__room_number')
    readonly_fields = ('rating', 'comment', 'review_date')
    fieldsets = (
        (None, {'fields': ('guest_name', 'room', 'rating')}),
        ('Комментарий', {'fields': ('comment_preview', 'comment'), 'classes': ('collapse',)}),
        ('Дополнительно', {'fields': ('review_date',)}),
    )

    @admin.display(description='Превью комментария')
    def comment_preview(self, obj):
        return obj.comment[:50] + ('...' if len(obj.comment) > 50 else '')

    class RoomInline(admin.TabularInline):
        model = Room
        extra = 0


@admin.register(Amenity)
class AmenityAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'related_rooms_count')  # Отображение количества связанных комнат
    search_fields = ('name',)
    list_filter = ('name',)
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Дополнительно', {'fields': ('related_rooms_count',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('related_rooms_count',)  # Вычисляемое поле

    @admin.display(description='Количество связанных комнат')
    def related_rooms_count(self, obj):
        return obj.room_set.count()  # Подсчёт связанных комнат через ForeignKey
