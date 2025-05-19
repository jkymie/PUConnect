# project/core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),
    
    # Eventos
    path('eventos/', views.eventos_list, name='eventos_list'),
    path('eventos/<int:pk>/', views.evento_detail, name='evento_detail'),
    path('eventos/criar/', views.evento_create, name='evento_create'),
    path('eventos/<int:pk>/editar/', views.evento_edit, name='evento_edit'),
    path('eventos/<int:pk>/excluir/', views.evento_delete, name='evento_delete'),
    path('meus-eventos/', views.meus_eventos, name='meus-eventos'),
    
    # Inscrições
    path('eventos/<int:pk>/inscrever/', views.inscrever_evento, name='inscrever_evento'),
    path('eventos/<int:pk>/cancelar-inscricao/', views.cancelar_inscricao, name='cancelar_inscricao'),
    path('inscricoes/', views.inscricoes, name='inscricoes'),
    
    # Perfil
    path('perfil/', views.profile_view, name='profile'),
    path('perfil/editar/', views.profile_edit, name='profile_edit'),
    path('perfil/<str:username>/', views.profile_view_other, name='profile_other'),
]

