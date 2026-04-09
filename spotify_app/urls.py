from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("callback/", views.callback, name="callback"),
    path("api/spotify/token/", views.spotify_token, name="spotify_token"),
]
