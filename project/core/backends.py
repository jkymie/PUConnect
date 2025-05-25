from django.contrib.auth.backends import ModelBackend
from .models import User

class MatriculaBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        matricula = username or kwargs.get('matricula')
        try:
            user = User.objects.get(matricula=matricula)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None 