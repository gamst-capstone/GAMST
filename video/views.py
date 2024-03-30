from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import status

from .models import Video, Caption
from .serializers import VideoSerializer, CaptionSerializer
from config.settings import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, VIDEO_BUCKET

import boto3, uuid
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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

    @swagger_auto_schema(
        operation_description='Upload video',
        manual_parameters=[
            openapi.Parameter(
                'video',
                openapi.IN_FORM,
                description='video file',
                type=openapi.TYPE_FILE,
                required=True,
                format='binary'
            ),
            openapi.Parameter(
                'name',
                openapi.IN_FORM,
                description='video name',
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: 'Success',
            400: 'Bad Request',
        }
    )
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
    @swagger_auto_schema(
        operation_description='Get video detail',
        manual_parameters=[
            openapi.Parameter(
                'video_id',
                openapi.IN_QUERY,
                description='video id',
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            200: 'Success',
            400: 'Bad Request',
        }
    )
    def get(self, request, pk):
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
        file_url = f"https://{bucket}.s3.amazonaws.com/{file_uid}"
        return {
            'video_url': file_url,
            'status': 'success'
        }
    except Exception as e:
        return {
            'status': 'fail',
            'message': str(e)
        }
    

class ListCaption(APIView):
    @swagger_auto_schema(
        operation_description='List captions',
        manual_parameters=[
            openapi.Parameter(
                'video_id',
                openapi.IN_QUERY,
                description='video id',
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            200: 'Success',
            400: 'Bad Request',
        }
    )
    def get(self, request, pk):
        try:
            captions = Caption.objects.filter(video=pk).order_by('frame_number')
            serializer = CaptionSerializer(captions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class InsertCaption(APIView):
    @swagger_auto_schema(
        operation_description='Insert caption',
        manual_parameters=[
            openapi.Parameter(
                'video_url',
                openapi.IN_FORM,
                description='video url',
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                'frame_number',
                openapi.IN_FORM,
                description='frame number',
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                'sentence',
                openapi.IN_FORM,
                description='sentence',
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: 'Success',
            400: 'Bad Request',
        }
    )
    def post(self, request):
        try:
            video = Video.objects.get(url=request.data.get('video_url'))

            caption = Caption.objects.create(
                video=video,  # 여기서 video 객체를 찾아서 저장해야 
                frame_number=request.data.get('frame_number'),
                sentence=request.data.get('sentence'),
                detected_object=request.data.get('detected_object')
            )
            serializer = CaptionSerializer(caption)
            return Response(serializer.data)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)