from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import status

from .models import Video
from .serializers import VideoSerializer
from config.settings import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, VIDEO_BUCKET
from django.shortcuts import render

import boto3, uuid
from rest_framework.decorators import api_view

@api_view(['GET'])
def index(request):
    context = {'message': "Health good"}
    return Response(context, status=status.HTTP_200_OK)

class ListVideo(APIView):
    def get(self, request):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)
    
class UploadVideo(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        try:
            video_obj = request.FILES['video']
            video_name = request.data.get('name')
            video_uid = str(uuid.uuid4())

            # upload video to s3 bucket
            res = upload_to_s3(video_obj, video_uid, VIDEO_BUCKET)
            if res['status'] == 'fail':
                return Response({'Error': res['message']}, status=status.HTTP_400_BAD_REQUEST)

            video = Video.objects.create(
                title=video_name,
                url=res['video_url']
            )
            serializer = VideoSerializer(video)
            return Response(serializer.data)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        

class VideoDetail(APIView):
    def get(self, pk):
        try:
            video = Video.objects.get(pk=pk)
            serializer = VideoSerializer(video)
            return Response(serializer.data)
        except Video.DoesNotExist:
            return Response({'Error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


def upload_to_s3(file, file_uid, bucket):
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    try:
        res = s3.upload_fileobj(file, bucket, file_uid)
        print(res)
        file_url = f"https://{bucket}.s3.amazonaws.com/{file_uid}"
        return {
            'video_url': file_url,
            'status': 'success'
        }
    except Exception as e:
        print(e)
        return {
            'status': 'fail',
            'message': str(e)
        }