from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import StreamingHttpResponse
from django.shortcuts import render

from .models import Video, Caption, RiskySection
from .serializers import VideoSerializer, CaptionSerializer, RiskSerializer
from config.settings import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, VIDEO_BUCKET
from config.sse_render import ServerSentEventRenderer

import boto3, uuid, asyncio
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from asgiref.sync import sync_to_async


@api_view(['GET'])
def index(request):
    context = {'message': "Health good"}
    return Response(context, status=status.HTTP_200_OK)

class AuthTestView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({'message': 'Authenticated'}, status=status.HTTP_200_OK)

class ListVideo(APIView):
    paginator_class = PageNumberPagination
    def get(self, request):
        try:
            queryset = Video.objects.all().order_by('id')
            paginator = self.paginator_class()
            results = paginator.paginate_queryset(queryset, request)
            serializer = VideoSerializer(results, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
        res = s3.upload_fileobj(
            file,
            bucket,
            file_uid,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
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
    pagination_class = PageNumberPagination
    parser_classes = (FormParser,)
    @swagger_auto_schema(
        operation_description='List captions',
        manual_parameters=[
            openapi.Parameter(
                'video_id',
                openapi.IN_PATH,
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
            queryset = Caption.objects.filter(video=pk).order_by('frame_number')
            paginator = self.pagination_class()
            results = paginator.paginate_queryset(queryset, request)
            serializer = CaptionSerializer(results, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
         

class StreamRiskList(APIView):
    renderer_classes = [ServerSentEventRenderer]

    @swagger_auto_schema(
        operation_description='List stream risk',
        manual_parameters=[
            openapi.Parameter(
                'video_id',
                openapi.IN_PATH,
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

    # 마지막에 추가된 row 반환
    @sync_to_async
    def get_queryset(self, last_object_id):
        queryset = RiskySection.objects.filter(video=self.kwargs['pk'])
        if last_object_id:
            queryset = queryset.filter(id__gt=last_object_id)
        # print(f"[^] {queryset} / {type(queryset)}")
        return list(queryset.order_by('id').values())

    async def get_objects(self, last_object_id):
        await asyncio.sleep(1)
        result = await self.get_queryset(last_object_id)
        if result:
            return result
        else:
            return []

    async def generate_object(self):
        last_object_id = None
        while True:
            objects = await self.get_objects(last_object_id)
            if objects:
                for object in objects:
                    yield f"data: {object}\n\n"
                last_object_id = objects[-1]['id']

    def get(self, request, pk):
        try:
            response = StreamingHttpResponse(self.generate_object(), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            response['Connection'] = 'keep-alive'
            return response
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ListRiskList(APIView):
    pagination_class = PageNumberPagination
    @swagger_auto_schema(
        operation_description='List risk',
        manual_parameters=[
            openapi.Parameter(
                'video_id',
                openapi.IN_PATH,
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
            queryset = RiskySection.objects.filter(video=pk).order_by('id')
            paginator = self.pagination_class()
            results = paginator.paginate_queryset(queryset, request)
            serializer = RiskSerializer(results, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




import random
from django.shortcuts import render
async def sse_stream(request):
    async def event_stream():
        test = ['a','b','c','d','e']
        i=0
        while True:
            yield f'data: {random.choice(test)} {i}\n\n'
            i+=1
            await asyncio.sleep(1)
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

def sse_test(request):
    return render(request, 'sse.html')
