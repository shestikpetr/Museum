from django.urls import path
from . import views

app_name = 'museum'

urlpatterns = [
    path('', views.exhibit_list, name='exhibit_list'),
    path('exhibit/<int:pk>/', views.exhibit_detail, name='exhibit_detail'),
]
