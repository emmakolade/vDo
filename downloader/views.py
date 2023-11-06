import os
import io
import re
import json
import zipfile
import requests
from .models import Video
from dotenv import load_dotenv
from rest_framework import status
from pytube import YouTube, Playlist
from django.http import FileResponse, HttpResponse
from .serializers import SearchSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils.encoding import smart_str


from .constants import ERROR, SUCCESS


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


def extract_playlist_id(search_query):
    # Extract the playlist ID from the URL if it's a valid YouTube playlist link
    if 'list=' in search_query:
        playlist_id = search_query.split('list=')[1].split('&')[0]
        return playlist_id
    return None


@api_view(['GET'])
def search_video(request):
    search_query = request.GET.get('q', '')

    if not search_query:
        return Response({'message': ERROR['SEARCH_EMPTY_QUERY_MESSAGE']}, status=status.HTTP_400_BAD_REQUEST)

    playlist_id = extract_playlist_id(search_query)

    if playlist_id:
        search_params = {
            'part': 'snippet',
            'key': str(os.getenv('API_KEY')),
            'maxResults': 5,
            'playlistId': playlist_id
        }
        search_url = 'https://www.googleapis.com/youtube/v3/playlistItems'

    # If it's not a playlist search, perform a regular video search
    else:
        search_params = {
            'part': 'snippet',
            'q': search_query,
            'type': 'video',
            'videoDefinition': 'any',
            'maxResults': 5,
            'key': 'AIzaSyD8PA1Zwa1va-80_qi-DMIMNEE3V2YNHLQ',
        }
        search_url = 'https://www.googleapis.com/youtube/v3/search'

    response = requests.get(search_url, params=search_params)

    if response.status_code != 200:
        return Response({'message': ERROR['SEARCH_API_FAILURE_MESSAGE']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    videos_data = response.json().get('items', [])

    if not videos_data:
        return Response({'message': ERROR['SEARCH_NO_RESULTS_MESSAGE']}, status=status.HTTP_404_NOT_FOUND)

    videos = []
    for video in videos_data:
        if playlist_id:
            video_id = video['snippet']['resourceId']['videoId']
        else:
            video_id = video['id']['videoId']
        title = video['snippet']['title']
        description = video['snippet']['description']
        thumbnail = video['snippet']['thumbnails']['high']['url']
        url = f'https://www.youtube.com/watch?v={video_id}'
        uploaded_date = video['snippet']['publishedAt']
        videos.append({
            'title': title,
            'description': description,
            'url': url,
            'thumbnail': thumbnail,
            'video_id': video_id,
            'uploaded_date': uploaded_date
        })

    return Response({'message': SUCCESS['SEARCH_SUCCESS_MESSAGE'], 'data': videos})


format_filters = {
    'mp3': {'only_audio': True, 'file_extension': 'mp4'},
    '720p': {'res': '720p', 'file_extension': 'mp4', 'progressive': True, 'type': 'video'},
    '1080p': {'res': '1080p', 'file_extension': 'mp4', 'progressive': False,  'type': 'video'},

}


@api_view(['GET'])
def download_video(request, video_url):
    try:

        # intialize youtube object
        yt = YouTube(video_url)

        # if format not in format_filters:
        #     return Response({'message': ERROR['INVALID_FORMAT']}, status=status.HTTP_400_BAD_REQUEST)

        # stream_filter = format_filters[format]
        # stream = yt.streams.filter(**stream_filter).first()

        stream = yt.streams.get_highest_resolution()
        video_file = stream.download()

        # Return the downloaded file as a response
        with open(video_file, 'rb') as file:
            response = FileResponse(file, as_attachment=True)
            response['Content-Disposition'] = f'attachment; filename={yt.title}.mp4'
            return response

    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def download_playlist(request, url, format):
    try:
        playlist = Playlist(url)

        if format not in format_filters:
            return Response({'message': ERROR['INVALID_FORMAT']}, status=status.HTTP_400_BAD_REQUEST)

        stream_filter = format_filters[format]

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for video in playlist.videos:
                stream = video.streams.filter(**stream_filter).first()
                video_data = stream.download()
                zipf.writestr(f'{video.title}.{format}', video_data)

        # Create a response with the zip content
        response = HttpResponse(zip_buffer.getvalue(),
                                content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={playlist.title}.zip'

        return response

    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def download_youtube_videos(request, video_id):
    try:
        youtube_url = f'https://www.youtube.com/watch?v={video_id}'

        yt = YouTube(youtube_url)
        stream = yt.streams.filter(
            progressive=True, file_extension='mp4').first()

        if not stream:
            return Response({'message': ERROR['NO_STREAM_AVAILABLE']}, status=status.HTTP_400_BAD_REQUEST)
            # Define the file name
        # file_name = f'{yt.title}.mp4'
        
        # # Set the content type to force download
        # response = HttpResponse(content_type='video/mp4')
        # response['Content-Disposition'] = f'attachment; filename="{smart_str(file_name)}"'
        # stream.stream_to_buffer(response)

        video_file = stream.download()
        response = FileResponse(open(video_file, 'rb'))
        response['Content-Disposition'] = f'attachment; filename={yt.title}.mp4'

        return response

    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
