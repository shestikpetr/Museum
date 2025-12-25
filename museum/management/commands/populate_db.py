from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from museum.models import Exhibit
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми экспонатами'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем заполнение базы данных...')

        # Создаем тестового пользователя для логирования
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'email': 'admin@museum.ru'
            }
        )
        if created:
            admin_user.set_password('admin')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Создан администратор: admin/admin'))

        # Данные для тестовых экспонатов
        categories = ['Живопись', 'Скульптура', 'Археология', 'Нумизматика', 'Этнография']
        locations = ['Зал №1', 'Зал №2', 'Зал №3', 'Запасник', 'Реставрационная мастерская']
        statuses = ['ON_DISPLAY', 'IN_STORAGE', 'IN_RESTORATION', 'ON_LOAN']

        exhibit_names = [
            ('Портрет императрицы', 'И.И. Иванов', 'Холст, масло', '80x60 см'),
            ('Античная ваза', 'Неизвестен', 'Керамика', '40x30 см'),
            ('Монета времен Петра I', 'Монетный двор', 'Серебро', '3x3 см'),
            ('Национальный костюм', 'Народные мастера', 'Ткань, вышивка', '-'),
            ('Бюст Александра I', 'П.П. Петров', 'Мрамор', '50x40x30 см'),
            ('Древнерусская икона', 'Монастырь', 'Дерево, темпера', '30x40 см'),
            ('Самовар фабрики Баташева', 'Баташев', 'Латунь', 'Высота 45 см'),
            ('Меч викингов', 'Неизвестен', 'Железо, бронза', '90 см'),
            ('Фарфоровый сервиз', 'ИФЗ', 'Фарфор', 'На 12 персон'),
            ('Картина "Закат"', 'С.С. Сидоров', 'Холст, масло', '100x120 см'),
        ]

        descriptions = [
            'Уникальный экспонат, представляющий большую историческую ценность. Был найден в ходе археологических раскопок.',
            'Данный предмет является прекрасным образцом мастерства своей эпохи. Отличается высоким качеством исполнения.',
            'Редкий экземпляр, один из немногих сохранившихся до наших дней. Имеет важное культурное значение.',
            'Экспонат находился в частной коллекции и был передан музею в дар. Представляет научный интерес.',
            'Замечательный пример искусства данного периода. Находится в отличном состоянии.',
        ]

        creation_dates = ['XVIII век', 'XIX век', 'XX век', '1850-е годы', '1920-е годы', '1700 г.', '1812 г.']

        created_count = 0
        for i in range(20):
            name_data = random.choice(exhibit_names)
            inv_number = f'МК-{2024}-{str(i+1).zfill(4)}'

            # Проверяем, не существует ли уже такой экспонат
            if Exhibit.objects.filter(inventory_number=inv_number).exists():
                continue

            exhibit = Exhibit.objects.create(
                inventory_number=inv_number,
                name=name_data[0],
                description=random.choice(descriptions),
                acquisition_date=date.today() - timedelta(days=random.randint(30, 3650)),
                status=random.choice(statuses),
                current_location=random.choice(locations),
                category=random.choice(categories),
                author=name_data[1],
                creation_date=random.choice(creation_dates),
                material=name_data[2],
                dimensions=name_data[3],
            )

            exhibit._changed_by = admin_user
            created_count += 1

            self.stdout.write(f'Создан экспонат: {exhibit.inventory_number} - {exhibit.name}')

        self.stdout.write(self.style.SUCCESS(f'\nГотово! Создано экспонатов: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Администратор: admin / admin'))
        self.stdout.write(self.style.SUCCESS(f'Теперь запустите сервер: python manage.py runserver'))
