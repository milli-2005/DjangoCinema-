from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),

    # Публичные страницы
    path('sessions/', views.movie_sessions, name='movie_sessions'),
    path('book/<int:session_id>/', views.book_session, name='book_session'),
    path('add-session/', views.add_session, name='add_session'),


    path('manage/', views.admin_panel, name='admin_panel'),

    # Управление сеансами (RUD)
    path('manage/sessions/', views.admin_sessions, name='admin_sessions'),
    path('manage/sessions/edit/<int:session_id>/', views.edit_session, name='edit_session'),
    path('manage/sessions/delete/<int:session_id>/', views.delete_session, name='delete_session'),

    # Управление бронированиями
    path('manage/bookings/', views.admin_bookings, name='admin_bookings'),
    path('manage/bookings/edit/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('manage/bookings/delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),

    # Управление пользователями
    path('manage/users/', views.admin_users, name='admin_users'),
    path('manage/users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('manage/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
]