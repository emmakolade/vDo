from django.db import models


class Video(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    thumbnail_url = models.URLField()
    video_url = models.URLField(unique=True)
    video_id = models.CharField(max_length=40, unique=True)
    downloaded_date = models.DateTimeField(auto_now_add=True)
    uploaded_date = models.DateTimeField()

    def __str__(self):
        return self.title
