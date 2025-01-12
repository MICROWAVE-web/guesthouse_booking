from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import (
    AmenityViewSet,
    RoomViewSet,
    GuestViewSet,
    BookingViewSet,
    PaymentViewSet,
    ReviewViewSet,
)

# Основные маршруты
urlpatterns = [
      path('admin/', admin.site.urls),
      path('', views.index, name='index'),
      path('login/', views.login_view, name='login'),
      path('logout/', views.logout_view, name='logout'),
      path('register/', views.register_view, name='register'),
      path('book_room/', views.book_room, name='book_room'),
      path('reviews/', views.review_list, name='review_list'),
      path('reviews/add/', views.add_review, name='add_review'),
      path('reviews/modal/', views.review_modal, name='review_modal'),
      path('reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),
      path('add_room/', views.add_room, name='add_room'),
      path('edit-room/<int:pk>/', views.edit_room, name='edit_room'),
      path('delete-room/<int:pk>/', views.delete_room, name='delete_room'),
  ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# REST Роутер
router = DefaultRouter()
router.register(r'amenities', AmenityViewSet, basename='amenity')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'guests', GuestViewSet, basename='guest')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'reviews', ReviewViewSet, basename='review')

# Добавляем маршруты API в /api/
urlpatterns += [
    path('api/', include(router.urls)),  # <-- Оборачиваем роутер в /api/
]
