from .views import index
from django.urls import path

app_name = 'frontend'

urlpatterns = [
    path('', index, name=''),
    path('join/', index, name='join'),
    path('create/', index, name='create'),
    path('room/<str:roomCode>/', index, name='room'),
]
