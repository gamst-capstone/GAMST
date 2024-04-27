from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token

from .serializers import UserRegisterSerializer, UserLoginSerializer
from .models import User
class UserRegisterView(APIView):
    def post(self, request: Request) -> Response:
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token: Token = TokenObtainPairSerializer.get_token(user)
            res = Response({
                "user": serializer.data,
                "message": "User created successfully",
                "token": {
                    "access": str(token.access_token),
                    "refresh": str(token)
                },
            }, status=status.HTTP_200_OK)
            return res
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLoginView(APIView):
    def post(self, request):
        token_serializer = TokenObtainPairSerializer(data=request.data)
        if token_serializer.is_valid():
            user = token_serializer.user
            print(user)
            serializer = UserLoginSerializer(user)
            res = Response({
                "user": serializer.data,
                "message": "User logged in successfully",
                "token": token_serializer.validated_data,
            }, status=status.HTTP_200_OK)
            
            res.set_cookie('refresh_token', str(token_serializer.validated_data['refresh']))
            res.set_cookie('access_token', str(token_serializer.validated_data['access']))
            return res 
        return Response(token_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserList(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        users = User.objects.all()
        serializer = UserLoginSerializer(users, many=True)
        return Response(serializer.data)