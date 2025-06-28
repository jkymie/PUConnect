# project/core/urls.py
from django.urls import path
from . import views
from .views import eventos_api

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('preferencias/', views.preferencias, name='preferencias'),
    
    # Eventos
    path('eventos/criar/', views.criar_evento, name='criar_evento'),
    path('eventos/<int:pk>/editar/', views.editar_evento, name='editar_evento'),
    path('eventos/<int:pk>/excluir/', views.excluir_evento, name='excluir_evento'),
    path('meus-eventos/', views.meus_eventos, name='meus_eventos'),
    
    # Inscrições
    path('eventos/<int:pk>/inscrever/', views.inscrever_evento, name='inscrever_evento'),
    path('eventos/<int:pk>/cancelar-inscricao/', views.cancelar_inscricao, name='cancelar_inscricao'),
    
    # Perfil
    path('perfil/editar/', views.profile_edit, name='profile_edit'),
    path('perfil/<str:username>/', views.profile_view_other, name='profile_other'),
    
    path('meus-eventos-aluno/', views.meus_eventos_aluno, name='meus_eventos_aluno'),
    path('eventos/', views.eventos_list, name='eventos_list'),
    path('evento/<int:pk>/', views.evento_detail, name='evento_detail'),
    path('evento/create/', views.evento_create, name='evento_create'),
    path('evento/<int:pk>/edit/', views.evento_edit, name='evento_edit'),
    path('evento/<int:pk>/delete/', views.evento_delete, name='evento_delete'),
    path('api/eventos/', eventos_api, name='eventos_api'),
    path('api/centros/', views.centros_api, name='centros_api'),
    # Recuperação de senha via modal
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/verify/', views.password_reset_verify, name='password_reset_verify'),
    path('password-reset/new/', views.password_reset_new, name='password_reset_new'),
    path('register-modal/', views.register_modal, name='register_modal'),
    path('login-modal/', views.login_modal, name='login_modal'),
]

