from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from .views import add_room, edit_room


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
    path('add_room/', add_room, name='add_room'),  
    path('edit-room/<int:pk>/', views.edit_room, name='edit_room'),
    path('delete-room/<int:pk>/', views.delete_room, name='delete_room'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

