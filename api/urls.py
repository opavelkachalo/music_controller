from django.urls import path
from .views import RoomView, CreateRoomView, GetRoomView
urlpatterns = [
    path('', RoomView.as_view(), name='home'),
    path('create-room/', CreateRoomView.as_view(), name='create-room'),
    path('get-room/', GetRoomView.as_view(), name='get-room'),
]
