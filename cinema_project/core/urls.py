from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('sessions/', views.movie_sessions, name='movie_sessions'),
    path('book/<int:session_id>/', views.book_session, name='book_session'),
    path('add-session/', views.add_session, name='add_session'),
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
]