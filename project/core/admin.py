from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Evento, Categoria

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informações adicionais', {
            'fields': ('curso', 'telefone', 'tipo_usuario', 'cpf', 'matricula')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações adicionais', {
            'fields': ('curso', 'telefone', 'tipo_usuario', 'cpf', 'matricula')
        }),
    )

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Evento)
admin.site.register(Categoria)
