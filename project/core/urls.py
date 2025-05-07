# project/core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('inscricoes/', views.inscricoes, name='inscricoes'),
]

