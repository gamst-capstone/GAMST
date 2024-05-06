from rest_framework import serializers
from .models import *

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'

class CaptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caption
        fields = '__all__'

class RiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskySection
        fields = '__all__'