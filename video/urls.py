from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.ListVideo.as_view()),
    path('upload/',views.UploadVideo.as_view()),
    path('<int:pk>/',views.VideoDetail.as_view()),
]