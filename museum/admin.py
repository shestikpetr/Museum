from django.contrib import admin
from django.utils.html import format_html
from .models import Exhibit, ExhibitPhoto, ExhibitLog


class ExhibitPhotoInline(admin.TabularInline):
    """Inline для управления фотографиями экспоната"""
    model = ExhibitPhoto
    extra = 3
    fields = ('image', 'caption', 'is_main', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = 'Превью'


@admin.register(Exhibit)
class ExhibitAdmin(admin.ModelAdmin):
    """Администрирование экспонатов"""
    list_display = ('inventory_number', 'name', 'status_colored', 'current_location', 'category', 'updated_at')
    list_filter = ('status', 'category', 'acquisition_date')
    search_fields = ('inventory_number', 'name', 'description', 'author')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ExhibitPhotoInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('inventory_number', 'name', 'description', 'acquisition_date')
        }),
        ('Статус и местоположение', {
            'fields': ('status', 'current_location')
        }),
        ('Характеристики', {
            'fields': ('category', 'author', 'creation_date', 'material', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['move_to_storage', 'send_to_restoration', 'return_to_display', 'send_on_loan']

    def status_colored(self, obj):
        """Цветной статус для удобства"""
        colors = {
            'ON_DISPLAY': '#28a745',
            'IN_RESTORATION': '#ffc107',
            'IN_STORAGE': '#6c757d',
            'ON_LOAN': '#17a2b8',
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Статус'

    def save_model(self, request, obj, form, change):
        """Сохранение с передачей пользователя для логирования"""
        obj._changed_by = request.user
        super().save_model(request, obj, form, change)

    # Массовые действия
    @admin.action(description='Переместить в запасник')
    def move_to_storage(self, request, queryset):
        updated = 0
        for exhibit in queryset:
            if exhibit.status != 'IN_STORAGE':
                exhibit._changed_by = request.user
                exhibit.status = 'IN_STORAGE'
                exhibit.save()
                updated += 1
        self.message_user(request, f'Перемещено в запасник: {updated} экспонат(ов)')

    @admin.action(description='Отправить на реставрацию')
    def send_to_restoration(self, request, queryset):
        updated = 0
        for exhibit in queryset:
            if exhibit.status != 'IN_RESTORATION':
                exhibit._changed_by = request.user
                exhibit.status = 'IN_RESTORATION'
                exhibit.save()
                updated += 1
        self.message_user(request, f'Отправлено на реставрацию: {updated} экспонат(ов)')

    @admin.action(description='Вернуть на выставку')
    def return_to_display(self, request, queryset):
        updated = 0
        for exhibit in queryset:
            if exhibit.status != 'ON_DISPLAY':
                exhibit._changed_by = request.user
                exhibit.status = 'ON_DISPLAY'
                exhibit.save()
                updated += 1
        self.message_user(request, f'Возвращено на выставку: {updated} экспонат(ов)')

    @admin.action(description='Отправить в другой музей')
    def send_on_loan(self, request, queryset):
        updated = 0
        for exhibit in queryset:
            if exhibit.status != 'ON_LOAN':
                exhibit._changed_by = request.user
                exhibit.status = 'ON_LOAN'
                exhibit.save()
                updated += 1
        self.message_user(request, f'Отправлено в другой музей: {updated} экспонат(ов)')


@admin.register(ExhibitPhoto)
class ExhibitPhotoAdmin(admin.ModelAdmin):
    """Администрирование фотографий"""
    list_display = ('exhibit', 'caption', 'is_main', 'image_preview', 'uploaded_at')
    list_filter = ('is_main', 'uploaded_at')
    search_fields = ('exhibit__name', 'exhibit__inventory_number', 'caption')
    readonly_fields = ('uploaded_at', 'image_preview_large')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = 'Превью'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 500px;"/>', obj.image.url)
        return "Нет изображения"
    image_preview_large.short_description = 'Изображение'


@admin.register(ExhibitLog)
class ExhibitLogAdmin(admin.ModelAdmin):
    """Администрирование журнала (только для чтения)"""
    list_display = ('exhibit', 'action_type', 'from_status_display', 'to_status_display', 'timestamp', 'performed_by')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('exhibit__inventory_number', 'exhibit__name', 'notes')
    readonly_fields = ('exhibit', 'action_type', 'from_status', 'to_status',
                      'from_location', 'to_location', 'timestamp', 'notes', 'performed_by')
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def from_status_display(self, obj):
        if obj.from_status:
            status_dict = dict(Exhibit.STATUS_CHOICES)
            return status_dict.get(obj.from_status, obj.from_status)
        return '-'
    from_status_display.short_description = 'Из статуса'

    def to_status_display(self, obj):
        if obj.to_status:
            status_dict = dict(Exhibit.STATUS_CHOICES)
            return status_dict.get(obj.to_status, obj.to_status)
        return '-'
    to_status_display.short_description = 'В статус'


# Настройка заголовка админки
admin.site.site_header = 'Управление музейным комплексом'
admin.site.site_title = 'Музейный комплекс'
admin.site.index_title = 'Администрирование'
