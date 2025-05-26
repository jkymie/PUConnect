# project/core/urls.py
from django.urls import path
from . import views

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
]

