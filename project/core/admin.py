from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Evento, Centro, Inscricao, SolicitarOrganizador, UserProfile

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informações adicionais', {
            'fields': ('telefone', 'tipo_usuario', 'matricula')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações adicionais', {
            'fields': ('telefone', 'tipo_usuario', 'matricula')
        }),
    )

class CentroAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome']
    search_fields = ['codigo', 'nome']
    ordering = ['nome']

class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'organizador', 'data_hora', 'preco', 'vagas', 'tipo_evento', 'lugar']
    list_filter = ['preco', 'tipo_evento', 'lugar', 'horas_complementares', 'centros', 'criado_em']
    search_fields = ['titulo', 'descricao', 'local', 'organizador__username']
    date_hierarchy = 'data_hora'
    filter_horizontal = ['centros']
    readonly_fields = ['criado_em']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'imagem')
        }),
        ('Data e Local', {
            'fields': ('data_hora', 'local', 'lugar', 'tipo_evento')
        }),
        ('Centros e Organização', {
            'fields': ('centros', 'organizador', 'horas_complementares')
        }),
        ('Vagas e Preço', {
            'fields': ('vagas', 'preco', 'preco_info')
        }),
        ('Metadados', {
            'fields': ('criado_em',),
            'classes': ('collapse',)
        }),
    )

class InscricaoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'evento', 'data_inscricao', 'presente']
    list_filter = ['presente', 'data_inscricao']
    search_fields = ['usuario__username', 'evento__titulo']
    date_hierarchy = 'data_inscricao'

class SolicitarOrganizadorAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'status', 'data_solicitacao', 'data_resposta']
    list_filter = ['status', 'data_solicitacao']
    search_fields = ['usuario__username', 'motivo']
    readonly_fields = ['data_solicitacao']
    date_hierarchy = 'data_solicitacao'

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'curso', 'data_nascimento']
    search_fields = ['user__username', 'user__email', 'curso']
    list_filter = ['data_nascimento']

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Evento, EventoAdmin)
admin.site.register(Centro, CentroAdmin)
admin.site.register(Inscricao, InscricaoAdmin)
admin.site.register(SolicitarOrganizador, SolicitarOrganizadorAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
