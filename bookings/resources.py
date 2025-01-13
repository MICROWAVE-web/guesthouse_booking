from import_export import fields
from import_export.resources import ModelResource

from .models import Booking


class BookingResource(ModelResource):
    # Кастомное поле для полного имени гостя
    guest_name = fields.Field(column_name='Гость')

    # Кастомное поле для цены с символом валюты
    total_price = fields.Field(column_name='Цена')

    class Meta:
        model = Booking
        fields = ('id', 'guest_name', 'room__name', 'check_in', 'check_out', 'total_price', 'is_paid')
        export_order = ('id', 'guest_name', 'room__name', 'check_in', 'check_out', 'total_price', 'is_paid')

    def get_export_headers(self, selected_fields):
        """
        Переопределяем метод для задания заголовков по verbose_name
        """
        headers = []
        for field in selected_fields:
            model_fields = self.Meta.model._meta.get_fields()
            header = next((x.verbose_name for x in model_fields if x.name == field), field)
            headers.append(header)
        return headers

    def dehydrate_guest_name(self, booking):
        """
        Кастомизация поля guest_name.
        Возвращает полное имя гостя.
        """
        additional_text = ''
        if booking.guest.is_blocked:
            additional_text = 'ЗАБЛОКИРОВАН'
        return f"{booking.guest.first_name} {booking.guest.last_name} {booking.guest.phone_number} {additional_text}".strip()

    def dehydrate_total_price(self, booking):
        """
        Кастомизация поля total_price.
        Добавляет символ валюты.
        """
        return f"₽{booking.total_price}"

    def dehydrate_is_paid(self, booking):
        """
        Кастомизация поля is_paid.
        """
        if booking.is_paid:
            return "Оплачено"
        return "Не оплачено"
