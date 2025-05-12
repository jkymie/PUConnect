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
    path('evento/<int:evento_id>/', views.evento_detail, name='evento_detail'),
    path('evento/create/', views.evento_create, name='evento_create'),
    path('evento/<int:evento_id>/edit/', views.evento_edit, name='evento_edit'),
    path('evento/<int:evento_id>/inscrever/', views.inscrever_evento, name='inscrever_evento'),
    path('evento/<int:evento_id>/presenca/', views.marcar_presenca, name='marcar_presenca'),
    path('solicitar-organizador/', views.solicitar_organizador, name='solicitar_organizador'),
    path('minhas-solicitacoes/', views.minhas_solicitacoes, name='minhas_solicitacoes'),
    path('solicitacao/<int:solicitacao_id>/responder/', views.responder_solicitacao, name='responder_solicitacao'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view_other, name='profile_other'),
]

