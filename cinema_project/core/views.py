from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from .models import MovieSession, Booking
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages


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
    """Главная страница админ-панели со статистикой"""
    from django.utils import timezone

    total_users = User.objects.count()
    total_sessions = MovieSession.objects.count()
    total_bookings = Booking.objects.count()
    active_sessions = MovieSession.objects.filter(date__gte=timezone.now()).count()

    return render(request, 'core/admin_panel.html', {
        'total_users': total_users,
        'total_sessions': total_sessions,
        'total_bookings': total_bookings,
        'active_sessions': active_sessions,
    })
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
        image = request.FILES.get('image')  # Добавляем обработку изображения

        if all([title, description, date, duration, price, seats_available]):
            MovieSession.objects.create(
                title=title,
                description=description,
                date=date,
                duration=duration,
                price=price,
                seats_available=seats_available,
                image=image  # Сохраняем изображение
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


@staff_member_required
def admin_bookings(request):
    """Просмотр всех бронирований"""
    search_query = request.GET.get('search', '')
    bookings_list = Booking.objects.all().select_related('user', 'session').order_by('-booking_date')

    if search_query:
        bookings_list = bookings_list.filter(
            Q(user__username__icontains=search_query) |
            Q(session__title__icontains=search_query)
        )

    paginator = Paginator(bookings_list, 10)
    page = request.GET.get('page')
    bookings = paginator.get_page(page)

    return render(request, 'core/admin_bookings.html', {'bookings': bookings})


@staff_member_required
def edit_booking(request, booking_id):
    """Редактирование бронирования"""
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        seats = request.POST.get('seats')
        if seats and int(seats) > 0:
            # Вычисляем разницу в количестве мест
            old_seats = booking.seats
            new_seats = int(seats)
            difference = new_seats - old_seats

            # Проверяем, достаточно ли мест
            if booking.session.seats_available >= difference:
                booking.seats = new_seats
                booking.session.seats_available -= difference
                booking.session.save()
                booking.save()
                messages.success(request, 'Бронирование успешно обновлено!')
                return redirect('admin_bookings')
            else:
                messages.error(request, 'Недостаточно свободных мест!')

    return render(request, 'core/edit_booking.html', {'booking': booking})


@staff_member_required
def delete_booking(request, booking_id):
    """Удаление бронирования"""
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        # Возвращаем места обратно
        booking.session.seats_available += booking.seats
        booking.session.save()
        booking.delete()
        messages.success(request, 'Бронирование успешно удалено!')
        return redirect('admin_bookings')

    return render(request, 'core/delete_booking.html', {'booking': booking})


@staff_member_required
def admin_users(request):
    """Просмотр всех пользователей"""
    search_query = request.GET.get('search', '')
    users_list = User.objects.all().order_by('date_joined')

    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    paginator = Paginator(users_list, 10)
    page = request.GET.get('page')
    users = paginator.get_page(page)

    return render(request, 'core/admin_users.html', {'users': users})


@staff_member_required
def edit_user(request, user_id):
    """Редактирование пользователя"""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        is_staff = request.POST.get('is_staff') == 'on'

        if username:
            user.username = username
        if email:
            user.email = email
        if first_name:
            user.first_name = first_name

        user.is_staff = is_staff
        user.save()
        messages.success(request, 'Пользователь успешно обновлен!')
        return redirect('admin_users')

    return render(request, 'core/edit_user.html', {'user': user})


@staff_member_required
def delete_user(request, user_id):
    """Удаление пользователя"""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Не позволяем удалить самого себя
        if user == request.user:
            messages.error(request, 'Вы не можете удалить свой собственный аккаунт!')
        else:
            user.delete()
            messages.success(request, 'Пользователь успешно удален!')
        return redirect('admin_users')

    return render(request, 'core/delete_user.html', {'user': user})


@staff_member_required
def admin_sessions(request):
    """Управление сеансами (RUD)"""
    search_query = request.GET.get('search', '')
    sessions_list = MovieSession.objects.all().order_by('date')

    if search_query:
        sessions_list = sessions_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    paginator = Paginator(sessions_list, 10)
    page = request.GET.get('page')
    sessions = paginator.get_page(page)

    return render(request, 'core/admin_sessions.html', {'sessions': sessions})


@staff_member_required
def edit_session(request, session_id):
    """Редактирование сеанса"""
    session = get_object_or_404(MovieSession, id=session_id)

    if request.method == 'POST':
        # Получаем данные из формы
        session.title = request.POST.get('title')
        session.description = request.POST.get('description')
        session.date = request.POST.get('date')
        session.duration = request.POST.get('duration')
        session.price = request.POST.get('price')
        seats_available = request.POST.get('seats_available')

        # Проверяем, что новое количество мест не меньше уже забронированных
        booked_seats = session.booking_set.count()
        if int(seats_available) < booked_seats:
            messages.error(request,
                           f'Нельзя установить {seats_available} мест, так как уже забронировано {booked_seats} мест!')
            return render(request, 'core/edit_session.html', {'session': session})

        session.seats_available = seats_available

        # Обновляем изображение, если загружено новое
        if 'image' in request.FILES:
            session.image = request.FILES['image']

        session.save()
        messages.success(request, 'Сеанс успешно обновлен!')
        return redirect('admin_sessions')

    return render(request, 'core/edit_session.html', {'session': session})


@staff_member_required
def delete_session(request, session_id):
    """Удаление сеанса"""
    session = get_object_or_404(MovieSession, id=session_id)

    if request.method == 'POST':
        # Получаем информацию для сообщения
        session_title = session.title
        bookings_count = session.booking_set.count()

        # Удаляем сеанс (все связанные бронирования удалятся автоматически благодаря CASCADE)
        session.delete()

        messages.success(request, f'Сеанс "{session_title}" и {bookings_count} связанных бронирований удалены!')
        return redirect('admin_sessions')

    return render(request, 'core/delete_session.html', {'session': session})