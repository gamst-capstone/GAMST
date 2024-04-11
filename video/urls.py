from django.urls import path
from . import views

urlpatterns = [
    # Videos
    path('', views.ListVideo.as_view()),
    path('upload/',views.UploadVideo.as_view()),
    path('<int:pk>/',views.VideoDetail.as_view()),

    # Captions
    path('<int:pk>/captions/', views.ListCaption.as_view()),
    path('<int:pk>/stream/', views.StreamRiskList.as_view()),
    path('sse/', views.sse_test, name='sse_test'),
    path('stream/test/', views.sse_stream, name='sse_stream'),
]