from django.db import models
from django.contrib.auth.models import User


class Exhibit(models.Model):
    """Модель экспоната"""

    STATUS_CHOICES = [
        ('ON_DISPLAY', 'На выставке'),
        ('IN_RESTORATION', 'На реставрации'),
        ('IN_STORAGE', 'В запаснике'),
        ('ON_LOAN', 'В другом музее'),
    ]

    inventory_number = models.CharField(
        'Инвентарный номер',
        max_length=100,
        unique=True,
        help_text='Уникальный инвентарный номер экспоната'
    )
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')
    acquisition_date = models.DateField('Дата поступления')
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='IN_STORAGE'
    )
    current_location = models.CharField(
        'Текущее местоположение',
        max_length=255,
        help_text='Зал, музей, реставрационная мастерская и т.д.'
    )

    # Дополнительные характеристики
    category = models.CharField('Категория', max_length=100, blank=True)
    author = models.CharField('Автор/создатель', max_length=255, blank=True)
    creation_date = models.CharField(
        'Дата создания',
        max_length=100,
        blank=True,
        help_text='Может быть текстом, например "XVIII век"'
    )
    material = models.CharField('Материал', max_length=255, blank=True)
    dimensions = models.CharField('Размеры', max_length=255, blank=True)

    # Служебные поля
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Экспонат'
        verbose_name_plural = 'Экспонаты'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.inventory_number} - {self.name}"


class ExhibitPhoto(models.Model):
    """Модель фотографии экспоната"""

    exhibit = models.ForeignKey(
        Exhibit,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Экспонат'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='exhibits/%Y/%m/%d/'
    )
    caption = models.CharField('Подпись', max_length=255, blank=True)
    is_main = models.BooleanField(
        'Главное фото',
        default=False,
        help_text='Отображается в каталоге'
    )
    uploaded_at = models.DateTimeField('Загружено', auto_now_add=True)

    class Meta:
        verbose_name = 'Фотография экспоната'
        verbose_name_plural = 'Фотографии экспонатов'
        ordering = ['-is_main', '-uploaded_at']

    def __str__(self):
        return f"Фото: {self.exhibit.name}"


class ExhibitLog(models.Model):
    """Модель журнала истории перемещений и изменений"""

    ACTION_CHOICES = [
        ('STATUS_CHANGE', 'Изменение статуса'),
        ('LOCATION_CHANGE', 'Изменение местоположения'),
        ('SENT_TO_RESTORATION', 'Отправка на реставрацию'),
        ('RETURNED_FROM_RESTORATION', 'Возврат с реставрации'),
        ('SENT_TO_STORAGE', 'Перемещение в запасник'),
        ('SENT_ON_LOAN', 'Отправка в другой музей'),
        ('RETURNED_FROM_LOAN', 'Возврат из другого музея'),
        ('OTHER', 'Другое'),
    ]

    exhibit = models.ForeignKey(
        Exhibit,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='Экспонат'
    )
    action_type = models.CharField(
        'Тип действия',
        max_length=30,
        choices=ACTION_CHOICES
    )
    from_status = models.CharField('Из статуса', max_length=20, blank=True)
    to_status = models.CharField('В статус', max_length=20, blank=True)
    from_location = models.CharField('Откуда', max_length=255, blank=True)
    to_location = models.CharField('Куда', max_length=255, blank=True)
    timestamp = models.DateTimeField('Дата и время', auto_now_add=True)
    notes = models.TextField('Примечания')
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Кто выполнил'
    )

    class Meta:
        verbose_name = 'Запись журнала'
        verbose_name_plural = 'Журнал истории'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.exhibit.inventory_number} - {self.get_action_type_display()} ({self.timestamp.strftime('%d.%m.%Y %H:%M')})"
