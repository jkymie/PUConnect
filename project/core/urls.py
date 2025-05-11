# project/core/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('inscricoes/', views.inscricoes, name='inscricoes'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('eventos/', views.eventos_list, name='eventos_list'),
    path('eventos/novo/', views.evento_create, name='evento_create'),
]

