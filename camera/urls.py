from django.urls import path
from . import views

urlpatterns = [
    # Cameras
    path('', views.ListCamera.as_view(), name='list_camera'),
    path('add/', views.CreateCamera.as_view(), name='add_camera'),
    path('<int:pk>/', views.DetailCamera.as_view(), name='detail_camera'),
    
    # Captions
    path('<int:pk>/captions/', views.ListCaption.as_view(), name='list_caption'),
    
    # Risky Sections
    path('<int:pk>/stream/', views.StreamRiskList.as_view(), name='stream_risk'),
    path('<int:pk>/risk/', views.ListRisk.as_view(), name='list_risk'),
]