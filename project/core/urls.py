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
    path('logout/', views.logout_view, name='logout'),
    path('eventos/', views.eventos_list, name='eventos_list'),
    path('eventos/novo/', views.evento_create, name='evento_create'),
    path('eventos/<int:evento_id>/inscrever/', views.inscrever_evento, name='inscrever_evento'),
    path('eventos/<int:evento_id>/presenca/', views.marcar_presenca, name='marcar_presenca'),
    path('solicitar-organizador/', views.solicitar_organizador, name='solicitar_organizador'),
    path('solicitacoes/', views.minhas_solicitacoes, name='minhas_solicitacoes'),
    path('solicitacoes/<int:solicitacao_id>/responder/', views.responder_solicitacao, name='responder_solicitacao'),
]

