from core.models import User

def sync_username_with_matricula():
    for u in User.objects.all():
        if u.username != u.matricula:
            print(f'Ajustando usuário {u.id}: username {u.username} -> {u.matricula}')
            u.username = u.matricula
            u.save()
    print('Sincronização concluída.')

if __name__ == '__main__':
    sync_username_with_matricula() 