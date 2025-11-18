import os
import django
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import MovieSession


class Command(BaseCommand):
    help = 'Fill database with sample movie sessions'

    def handle(self, *args, **options):
        # Очищаем существующие сеансы
        MovieSession.objects.all().delete()

        # Создаем тестовые сеансы
        sessions_data = [
            {
                'title': 'Аватар: Путь воды',
                'description': 'Джейк Салли и Нейтири создали семью, но им вновь угрожают люди с Земли. Чтобы защитить родную планету, им придется отправиться в разные уголки Пандоры и найти поддержку у других кланов Нави.',
                'duration': 192,
                'price': 550.00,
                'seats_available': 120,
            },
            {
                'title': 'Оппенгеймер',
                'description': 'История жизни американского физика-теоретика Роберта Оппенгеймера, который в годы Второй мировой войны руководил Манхэттенским проектом — программой по созданию атомной бомбы.',
                'duration': 180,
                'price': 480.00,
                'seats_available': 80,
            },
            {
                'title': 'Барби',
                'description': 'Кукла Барби, живущая в идеальном мире Барбиленда, обнаруживает, что с ней что-то не так, и отправляется в реальный мир, чтобы найти ответы на свои вопросы.',
                'duration': 114,
                'price': 450.00,
                'seats_available': 95,
            },
            {
                'title': 'Джон Уик 4',
                'description': 'Джон Уик обнаруживает путь к победе над Правлением Кланов. Но прежде чем он сможет заслужить свободу, Уику предстоит сразиться с новым врагом и могущественными союзниками.',
                'duration': 169,
                'price': 500.00,
                'seats_available': 65,
            },
            {
                'title': 'Стражи Галактики: Часть 3',
                'description': 'Питер Квилл все еще не может смириться с потерей Гаморы и собирает свою команду, чтобы защитить Вселенную и одного из своих. Эта миссия может стать последней для Стражей.',
                'duration': 150,
                'price': 520.00,
                'seats_available': 110,
            },
            {
                'title': 'Человек-паук: Паутина вселенных',
                'description': 'Майлз Моралес переносится через Мультивселенную и встречает команду Людей-пауков, которые должны защитить само её существование.',
                'duration': 140,
                'price': 490.00,
                'seats_available': 75,
            },
            {
                'title': 'Трансформеры: Эпоха зверей',
                'description': 'Оптимус Прайм и автоботы сталкиваются с самой страшной угрозой из всех, с которыми они когда-либо сталкивались: гигантской планетой-трансформером Юникроном.',
                'duration': 127,
                'price': 470.00,
                'seats_available': 85,
            },
            {
                'title': 'Миссия невыполнима: Смертельная расплата',
                'description': 'Итан Хант и его команда МВФ должны выследить ужасающее новое оружие, которое угрожает всему человечеству, если оно попадет не в те руки.',
                'duration': 163,
                'price': 510.00,
                'seats_available': 70,
            },
            {
                'title': 'Русалочка',
                'description': 'Ариэль, младшая дочь короля Тритона, влюбляется в принца-человека и заключает сделку с морской ведьмой, чтобы побывать в его мире.',
                'duration': 135,
                'price': 430.00,
                'seats_available': 100,
            },
            {
                'title': 'Флэш',
                'description': 'Барри Аллен использует свои суперспособности, чтобы путешествовать во времени и изменить прошлое, но его попытка спасти семью создает альтернативную реальность.',
                'duration': 144,
                'price': 460.00,
                'seats_available': 60,
            },
        ]

        # Создаем сеансы на ближайшие дни
        base_date = timezone.now() + timedelta(hours=2)  # Через 2 часа от текущего времени

        created_count = 0
        for i, session_data in enumerate(sessions_data):
            session_date = base_date + timedelta(days=i, hours=i * 2)

            MovieSession.objects.create(
                title=session_data['title'],
                description=session_data['description'],
                date=session_date,
                duration=session_data['duration'],
                price=session_data['price'],
                seats_available=session_data['seats_available'],
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {created_count} тестовых сеансов!')
        )