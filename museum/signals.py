from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Exhibit, ExhibitLog


@receiver(pre_save, sender=Exhibit)
def log_exhibit_changes(sender, instance, **kwargs):
    """
    Автоматическое логирование изменений статуса и местоположения экспоната
    """
    if not instance.pk:
        # Новый экспонат, не логируем
        return

    try:
        old_instance = Exhibit.objects.get(pk=instance.pk)
    except Exhibit.DoesNotExist:
        return

    # Проверяем изменение статуса
    if old_instance.status != instance.status:
        action_type = 'STATUS_CHANGE'
        notes = f'Изменен статус с "{old_instance.get_status_display()}" на "{instance.get_status_display()}"'

        # Определяем конкретный тип действия
        if instance.status == 'IN_RESTORATION':
            action_type = 'SENT_TO_RESTORATION'
        elif old_instance.status == 'IN_RESTORATION' and instance.status == 'ON_DISPLAY':
            action_type = 'RETURNED_FROM_RESTORATION'
        elif instance.status == 'IN_STORAGE':
            action_type = 'SENT_TO_STORAGE'
        elif instance.status == 'ON_LOAN':
            action_type = 'SENT_ON_LOAN'
        elif old_instance.status == 'ON_LOAN':
            action_type = 'RETURNED_FROM_LOAN'

        # Создаем запись в журнале
        ExhibitLog.objects.create(
            exhibit=instance,
            action_type=action_type,
            from_status=old_instance.status,
            to_status=instance.status,
            from_location=old_instance.current_location,
            to_location=instance.current_location,
            notes=notes,
            performed_by=getattr(instance, '_changed_by', None)
        )

    # Проверяем изменение местоположения (если статус не изменился)
    elif old_instance.current_location != instance.current_location:
        notes = f'Изменено местоположение с "{old_instance.current_location}" на "{instance.current_location}"'

        ExhibitLog.objects.create(
            exhibit=instance,
            action_type='LOCATION_CHANGE',
            from_status=old_instance.status,
            to_status=instance.status,
            from_location=old_instance.current_location,
            to_location=instance.current_location,
            notes=notes,
            performed_by=getattr(instance, '_changed_by', None)
        )
