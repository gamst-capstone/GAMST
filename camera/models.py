from django.db import models

class Camera(models.Model):
    name = models.CharField(max_length=100)
    stream_url = models.URLField(max_length=200)
    def __str__(self):
        return self.name
    

class Caption(models.Model):
    SENTIMENT_CHOICES = (
        ('P', 'Positive'),
        ('N', 'Negative'),
        ('U', 'Unknown'),
    )
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    sentence = models.TextField(null=True)
    sentiment_score = models.TextField(null=True)
    sentiment_result = models.CharField(max_length=1, choices=SENTIMENT_CHOICES, default='U', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class RiskySection(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    video_uid = models.TextField(null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)