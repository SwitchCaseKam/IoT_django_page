from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='blog-home'),
    path('analysis/', views.analysis, name='blog-analysis'),
    path('about/', views.about, name='blog-about'),
]
