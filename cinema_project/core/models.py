from django.db import models
from django.contrib.auth.models import User


class MovieSession(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название фильма")
    description = models.TextField(verbose_name="Описание")
    date = models.DateTimeField(verbose_name="Дата и время сеанса")
    duration = models.IntegerField(verbose_name="Продолжительность (мин)")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    seats_available = models.IntegerField(verbose_name="Доступные места")
    image = models.ImageField(upload_to='movies/', null=True, blank=True, verbose_name="Постер")

    def __str__(self):
        return f"{self.title} - {self.date}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(MovieSession, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    seats = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.session.title}"