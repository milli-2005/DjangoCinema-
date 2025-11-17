from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import CustomUserCreationForm
from .models import MovieSession, Booking
from django.core.paginator import Paginator
from django.db.models import Q


def is_admin(user):
    return user.is_staff


def index(request):
    return render(request, 'core/index.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()

    return render(request, 'core/register.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_panel')
            return redirect('profile')
        else:
            # Добавляем сообщение об ошибке
            return render(request, 'core/login.html', {'error': 'Неверный логин или пароль'})

    return render(request, 'core/login.html')


@login_required
def profile(request):
    user_bookings = Booking.objects.filter(user=request.user).select_related('session')
    return render(request, 'core/profile.html', {'bookings': user_bookings})


@staff_member_required
def admin_panel(request):
    all_bookings = Booking.objects.all().select_related('user', 'session')
    return render(request, 'core/admin_panel.html', {'bookings': all_bookings})


def movie_sessions(request):
    search_query = request.GET.get('search', '')
    sessions_list = MovieSession.objects.all().order_by('date')

    if search_query:
        sessions_list = sessions_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    paginator = Paginator(sessions_list, 6)
    page = request.GET.get('page')
    sessions = paginator.get_page(page)

    return render(request, 'core/movie_sessions.html', {'sessions': sessions})


@login_required
def book_session(request, session_id):
    session = get_object_or_404(MovieSession, id=session_id)

    if request.method == 'POST':
        if session.seats_available > 0:
            # Проверяем, не забронировал ли пользователь уже этот сеанс
            existing_booking = Booking.objects.filter(user=request.user, session=session).first()
            if not existing_booking:
                Booking.objects.create(user=request.user, session=session)
                session.seats_available -= 1
                session.save()
                return redirect('profile')
            else:
                # Пользователь уже забронировал этот сеанс
                return render(request, 'core/book_session.html', {
                    'session': session,
                    'error': 'Вы уже забронировали этот сеанс'
                })

    return render(request, 'core/book_session.html', {'session': session})


@staff_member_required
def add_session(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        duration = request.POST.get('duration')
        price = request.POST.get('price')
        seats_available = request.POST.get('seats_available')

        if all([title, description, date, duration, price, seats_available]):
            MovieSession.objects.create(
                title=title,
                description=description,
                date=date,
                duration=duration,
                price=price,
                seats_available=seats_available
            )
            return redirect('movie_sessions')

    return render(request, 'core/add_session.html')


@staff_member_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        # Возвращаем место обратно
        booking.session.seats_available += 1
        booking.session.save()
        booking.delete()
        return redirect('admin_panel')



from django.contrib.auth import logout as auth_logout
def custom_logout(request):
    auth_logout(request)
    return redirect('index')