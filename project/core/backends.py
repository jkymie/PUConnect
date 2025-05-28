from django.contrib.auth.backends import ModelBackend
from .models import User

class MatriculaBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Só aceita matrícula como identificador
        matricula = username
        print(f"[DEBUG] Tentando autenticar matrícula: {matricula}")
        try:
            user = User.objects.get(matricula=matricula)
        except User.DoesNotExist:
            print("[DEBUG] Matrícula não encontrada.")
            return None
        if user.check_password(password):
            print(f"[DEBUG] Login OK para matrícula: {matricula}")
            return user
        else:
            print(f"[DEBUG] Senha incorreta para matrícula: {matricula}")
        return None 