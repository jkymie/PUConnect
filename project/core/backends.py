from django.contrib.auth.backends import ModelBackend
from .models import User

class MatriculaBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        #para poder usar matrícula OU e-mail como identificador
        identificador = username
        user = None
        try:
            user = User.objects.get(matricula=identificador)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=identificador)
            except User.DoesNotExist:
                return None
        if user and user.check_password(password):
            return user
        return None 