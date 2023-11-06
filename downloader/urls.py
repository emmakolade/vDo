from django.urls import path
from .views import search_video, download_video, download_playlist, download_youtube_videos

urlpatterns = [
    path('search/', search_video, name='search'),
    path('downloads/<str:video_url>', download_video, name='downloads'),
    path('download/<str:video_id>', download_youtube_videos, name='download'),
    path('download/playlist', download_playlist, name='download_playlist')
]
