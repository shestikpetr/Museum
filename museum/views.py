from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Exhibit


def exhibit_list(request):
    """Каталог экспонатов (только те, что на выставке)"""
    exhibits = Exhibit.objects.filter(status='ON_DISPLAY').prefetch_related('photos')

    # Пагинация - 12 экспонатов на страницу
    paginator = Paginator(exhibits, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Статистика для отображения
    total_exhibits = Exhibit.objects.count()
    on_display = Exhibit.objects.filter(status='ON_DISPLAY').count()

    context = {
        'page_obj': page_obj,
        'total_exhibits': total_exhibits,
        'on_display': on_display,
    }
    return render(request, 'museum/exhibit_list.html', context)


def exhibit_detail(request, pk):
    """Страница экспоната с полной информацией"""
    exhibit = get_object_or_404(
        Exhibit.objects.prefetch_related('photos', 'history__performed_by'),
        pk=pk
    )

    # Получаем историю перемещений
    history = exhibit.history.all()[:10]  # Последние 10 записей

    context = {
        'exhibit': exhibit,
        'photos': exhibit.photos.all(),
        'main_photo': exhibit.photos.filter(is_main=True).first() or exhibit.photos.first(),
        'history': history,
    }
    return render(request, 'museum/exhibit_detail.html', context)
