from rest_framework import serializers
from .models import Evento, Centro

class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = ['id', 'titulo', 'data_hora', 'local', 'imagem']

class CentroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Centro
        fields = ['id', 'codigo', 'nome'] 