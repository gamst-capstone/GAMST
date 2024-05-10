from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import StreamingHttpResponse

from .models import Camera, Caption, RiskySection
from .serializers import CameraSerializer, CaptionSerializer, RiskSerializer
from config.settings import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY
from config.sse_render import ServerSentEventRenderer, CustomJSONEncoder

import boto3, uuid, asyncio, json
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from urllib.parse import urlparse
from asgiref.sync import sync_to_async


class ListCamera(APIView):
    paginator_class = PageNumberPagination
    @swagger_auto_schema(
        operation_description="카메라 목록 조회",
        responses={
            200: "Success",
            400: "Bad Request"
        },
    )
    def get(self, request):
        try:
            queryset = Camera.objects.all().order_by('id')
            paginator = self.paginator_class()
            results = paginator.paginate_queryset(queryset, request)
            serializer = CameraSerializer(results, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class CreateCamera(APIView):
    @swagger_auto_schema(
        operation_description='Create Camera',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'url'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'url': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: 'Success',
            400: 'Bad Request',
        }
    )
    def post(self, request):
        try:
            camera_name = request.data.get('name')
            url = request.data.get('url')

            # validation check
            if not validate_camera_url(url):
                return Response({'Error': 'Invalid URL'}, status=status.HTTP_400_BAD_REQUEST)
            
            camera = Camera.objects.create(
                name=camera_name,
                stream_url=url,
            )
            serializer = CameraSerializer(camera)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

def validate_camera_url(url):
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ['http', 'https', 'rtsp']:
            return False
        # TODO : 실제 카메라 Stream URL인지 검증 로직
        return True
    except Exception as e:
        return False
    
class DetailCamera(APIView):
    @swagger_auto_schema(
        operation_description="카메라 상세 조회",
        manual_parameters=[
            openapi.Parameter(
                'camera_id',
                openapi.IN_PATH,
                description='camera_id',
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            200: "Success",
            400: "Bad Request",
            404: "Camera not found",
        },
    )
    def get(self, request, pk):
        try:
            camera = Camera.objects.get(id=pk)
            serializer = CameraSerializer(camera)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Camera.DoesNotExist:
            return Response({'Error': 'Camera not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class ListCaption(APIView):
    pagination_class = PageNumberPagination
    @swagger_auto_schema(
        operation_description='List captions',
        manual_parameters=[
            openapi.Parameter(
                'camera_id',
                openapi.IN_PATH,
                description='camera_id',
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
            queryset = Caption.objects.filter(video=pk).order_by('start_time')
            paginator = self.pagination_class()
            results = paginator.paginate_queryset(queryset, request)
            serializer = CaptionSerializer(results, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class StreamRiskList(APIView):
    renderer_classes = [ServerSentEventRenderer]

    @swagger_auto_schema(
        operation_description='Stream risk',
        responses={
            200: 'Success',
            400: 'Bad Request',
        }
    )

    @sync_to_async
    def get_queryset(self, last_object_id):
        queryset = RiskySection.objects.all()
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
                    object = json.dumps(object, cls=CustomJSONEncoder)
                    yield f"data: {object}\n\n"
                last_object_id = objects[-1]['id']

    def get(self, request):
        try:
            response = StreamingHttpResponse(self.generate_object(), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            response['Connection'] = 'keep-alive'
            return response
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ListRisk(APIView):
    pagination_class = PageNumberPagination
    @swagger_auto_schema(
        operation_description='List risk',
        manual_parameters=[
            openapi.Parameter(
                'camera_id',
                openapi.IN_PATH,
                description='camera id',
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
            queryset = RiskySection.objects.filter(camera=pk).order_by('id')
            paginator = self.pagination_class()
            results = paginator.paginate_queryset(queryset, request)
            serializer = RiskSerializer(results, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)