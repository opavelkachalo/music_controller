from django.urls import path
from .views import AuthUrl, spotify_callback, IsAuthenticated

urlpatterns = [
    path('get-auth-url/', AuthUrl.as_view()),
    path('redirect/', spotify_callback),
    path('is-authenticated/', IsAuthenticated.as_view()),
]
