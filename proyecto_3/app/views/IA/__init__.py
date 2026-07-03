from django.urls import path
from . import views

urlpatterns = [
    path('', views.ia_index, name='ia_index'),
    path('chat/', views.ia_chat, name='ia_chat'),
]