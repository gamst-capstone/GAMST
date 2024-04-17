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
from .serializers import CameraSerializer, CaptionSerializer, RiskySectionSerializer
from config.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from config.sse_render import ServerSentEventRenderer

import boto3, uuid, asyncio
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
    def post(self, request):
        try:
            camera_name = request.data.get('name')
            url = request.data.get('url')

            # validation check
            if not validate_camera_url(url):
                return Response({'Error': 'Invalid URL'}, status=status.HTTP_400_BAD_REQUEST)
            
            camera = Camera.objects.create(
                name=camera_name,
                url=url,
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
    def get(self, request, camera_id):
        try:
            camera = Camera.objects.get(id=camera_id)
            serializer = CameraSerializer(camera)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Camera.DoesNotExist:
            return Response({'Error': 'Camera not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class ListCaption(APIView):
    pagination_class = PageNumberPagination
    parser_classes = (FormParser,)
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
        if not last_object_id:
            queryset = RiskySection.objects.filter(
                video=self.kwargs['pk']
            ).order_by('id').values().first()
            print(f">>>>>>>> first row of {self.kwargs['pk']}")
        else:
            queryset = RiskySection.objects.filter(
                video=self.kwargs['pk'],
                id=last_object_id,
                ).order_by('id').values().last()
            print(f">>>>>>>> {self.kwargs['pk']} / {last_object_id}")
        return queryset

    async def get_objects(self, last_object_id):
        await asyncio.sleep(1)
        result = await self.get_queryset(last_object_id)
        # result = RiskySection.objects.filter(video=self.kwargs['pk']).last()
        if result:
            print(f"{result} / {last_object_id}")
            return result
        else:
            print('no result')
            return {}

    async def generate_object(self):
        last_object_id = None
        while True:
            object = await self.get_objects(last_object_id)
            if object:
                yield f"data: {object}\n\n"
                last_object_id = object['id'] + 1

    def get(self, request, pk):
        try:
            response = StreamingHttpResponse(self.generate_object(), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            response['Connection'] = 'keep-alive'
            return response
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
