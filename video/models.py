from django.db import models
from django.urls import reverse

class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    url = models.CharField(max_length=200)
    thumbnail = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('video-detail', args=[str(self.id)])
    

class Caption(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    frame_number = models.IntegerField()
    sentence = models.TextField()
    detected_object = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text