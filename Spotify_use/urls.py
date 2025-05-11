"""
URL configuration for Spotify_use project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# from django.urls import path
from django.urls import path, include
from app.views import SpotifyAuthorize, SpotifyCallback, SpotifyData, SpotifyPlay, SpotifyStop



# urls.py (include in your main project urls)



urlpatterns = [
    # ...
    path('admin/', admin.site.urls),
    path('spotify/authorize/', SpotifyAuthorize.as_view(), name='sp-authorize'),
    path('spotify/callback/',  SpotifyCallback.as_view(),  name='sp-callback'),
    path('spotify/',           SpotifyData.as_view(),      name='sp-data'),
    path('spotify/play/',      SpotifyPlay.as_view(),      name='sp-play'),
    path('spotify/stop/',      SpotifyStop.as_view(),      name='sp-stop'),
]

