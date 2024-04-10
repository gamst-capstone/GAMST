from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.ListVideo.as_view()),
    path('upload/',views.UploadVideo.as_view()),
    path('<int:pk>/',views.VideoDetail.as_view()),

    path('caption/insert/', views.InsertCaption.as_view()),
    path('caption/list/<int:pk>', views.ListCaption.as_view()),
    path('stream/<int:pk>', views.StreamRiskList.as_view()),
    path('sse/', views.sse_test, name='sse_test'),
    path('stream/test/', views.sse_stream, name='sse_stream'),
]