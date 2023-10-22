import json
import requests
from .models import Video
from pytube import YouTube
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def search_video(request):
    search_query = request.GET.get('q', '')
