from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Room
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Review, Room, Booking
from .forms import ReviewForm
from .forms import RoomForm
from django.contrib.auth.forms import UserCreationForm
from .forms import BookingForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import datetime

def index(request):
    rooms = Room.objects.all()
    return render(request, 'bookings/index.html', {'rooms': rooms})

def login_view(request):
    print(1)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Неверные логин или пароль')
    return redirect('index')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Пользователь с таким логином уже существует')
    return redirect('index')

def logout_view(request):
    print(2)
    logout(request)
    return redirect('index')

@login_required
@csrf_exempt
def book_room(request):
    if request.method == 'POST':
        fio = request.POST.get('fio')
        phone_number = request.POST.get('phone_number')
        room_id = request.POST.get('room')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        first_name, last_name = fio.split()[:2]

        guest, created = Guest.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )

        room = get_object_or_404(Room, id=room_id)
        check_in_date = datetime.datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.datetime.strptime(check_out, '%Y-%m-%d').date()
        total_price = room.price_per_night * (check_out_date - check_in_date).days

        Booking.objects.create(
            guest=guest,
            room=room,
            check_in=check_in_date,
            check_out=check_out_date,
            total_price=total_price,
            booking_name=f"Booking for {fio}"
        )

        return JsonResponse({"message": "Заявка отправлена"})

    rooms = Room.objects.all()
    return render(request, 'bookings/book_room.html', {'rooms': rooms})

@login_required
def review_list(request):
    reviews = Review.objects.all()
    rooms = Room.objects.all()
    return render(request, 'bookings/review_list.html', {'reviews': reviews, 'rooms': rooms})

@csrf_exempt
@login_required
def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"message": "Отзыв успешно добавлен"})
            return redirect('review_list')
        else:
            print("Form is not valid")
    else:
        form = ReviewForm()
    return render(request, 'bookings/add_review.html', {'form': form})

@login_required
def review_modal(request):
    form = ReviewForm(initial={'guest_name': request.user.username})
    rooms = Room.objects.all()
    return render(request, 'bookings/review_modal.html', {'form': form, 'rooms': rooms})

@csrf_exempt
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user.is_staff:
        review.delete()
        messages.success(request, 'Отзыв успешно удален.')
    return redirect('review_list')

@login_required
def add_room(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = RoomForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('index')
        else:
            form = RoomForm()
        return render(request, 'bookings/add_room.html', {'form': form})
    else:
        return redirect('index')

@login_required
def edit_room(request, pk):
    if request.user.is_superuser:
        room = get_object_or_404(Room, pk=pk)
        if request.method == 'POST':
            form = RoomForm(request.POST, request.FILES, instance=room)
            if form.is_valid():
                form.save()
                return redirect('index')
        else:
            form = RoomForm(instance=room)
        return render(request, 'bookings/edit_room.html', {'form': form, 'room': room})
    else:
        return redirect('index')

def delete_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('index')  # После удаления перенаправляем на главную страницу или куда нужно
    
    return render(request, 'edit_room.html', {'room': room})
