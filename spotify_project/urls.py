from django.urls import path, include

urlpatterns = [
    path("", include("spotify_app.urls")),
]
