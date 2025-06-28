from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from .forms import UserRegistrationForm, UserLoginForm, EventoForm, UserProfileForm, EmailChangeForm
from .models import Evento, Inscricao, UserProfile, Centro
from django.contrib.auth.forms import PasswordChangeForm
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import EventoSerializer, CentroSerializer
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import JsonResponse
import random
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.urls import reverse
from datetime import date

User = get_user_model()

def index(request):
    # If there's a search query, redirect to events list with the query
    query = request.GET.get('q')
    if query:
        return redirect(f"{reverse('eventos_list')}?q={query}")
    return render(request, 'core/index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'core.backends.MatriculaBackend'
            auth_login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('index')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('index')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = UserLoginForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    # Usar um redirect temporário para garantir que as mensagens sejam exibidas
    response = redirect('index')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def is_organizador(user):
    return user.is_authenticated and user.tipo_usuario == 'organizador'

@login_required
@user_passes_test(is_organizador)
def evento_create(request):
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = request.user
            evento.save()
            form.save_m2m()  # Salva os campos ManyToMany como centros
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('meus-eventos')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = EventoForm()
    return render(request, 'core/evento_form.html', {'form': form, 'action': 'Criar'})

@login_required
@user_passes_test(is_organizador)
def evento_edit(request, pk):
    evento = get_object_or_404(Evento, pk=pk, organizador=request.user)
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('meus-eventos')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = EventoForm(instance=evento)
    return render(request, 'core/evento_form.html', {'form': form, 'action': 'Editar'})

@login_required
@user_passes_test(is_organizador)
def evento_delete(request, pk):
    evento = get_object_or_404(Evento, pk=pk, organizador=request.user)
    if request.method == 'POST':
        # Verifica se há inscrições
        if evento.inscricoes.exists():
            messages.error(request, 'Não é possível excluir um evento que possui inscrições.')
            return redirect('meus-eventos')
        evento.delete()
        messages.success(request, 'Evento excluído com sucesso!')
        return redirect('meus-eventos')
    return render(request, 'core/evento_confirm_delete.html', {'evento': evento})

@login_required
def inscrever_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if not evento.tem_vagas_disponiveis():
        messages.error(request, 'Desculpe, não há mais vagas disponíveis para este evento.')
        return redirect('eventos_list')
    
    if evento.esta_inscrito(request.user):
        messages.warning(request, 'Você já está seguindo este evento.')
        return redirect('eventos_list')
    
    Inscricao.objects.create(evento=evento, usuario=request.user)
    messages.success(request, 'Agora você está seguindo este evento!')
    return redirect('eventos_list')

@login_required
def cancelar_inscricao(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    inscricao = get_object_or_404(Inscricao, evento=evento, usuario=request.user)
    inscricao.delete()
    messages.success(request, 'Você deixou de seguir este evento.')
    return redirect('eventos_list')

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'core/profile_edit.html', {'form': form})

@login_required
def profile_view_other(request, username):
    user = get_object_or_404(User, username=username)
    user_profile = user.profile
    eventos_participados = user_profile.get_eventos_participados()
    eventos_organizados = user_profile.get_eventos_organizados()
    
    context = {
        'user_profile': user_profile,
        'eventos_participados': eventos_participados,
        'eventos_organizados': eventos_organizados,
        'total_participados': user_profile.get_total_eventos_participados(),
        'total_organizados': user_profile.get_total_eventos_organizados(),
    }
    return render(request, 'core/profile_other.html', context)

@login_required
def meus_eventos_view(request):
    return render(request, 'meus-eventos.html')

@login_required
def meus_eventos(request):
    if request.user.tipo_usuario != 'organizador':
        return redirect('index')
    
    try:
        eventos = Evento.objects.filter(organizador=request.user).order_by('-data_hora')
        
        # Search by query
        query = request.GET.get('q')
        if query:
            eventos = eventos.filter(
                Q(titulo__icontains=query) |
                Q(descricao__icontains=query) |
                Q(local__icontains=query)
            )
        
        return render(request, 'core/meus_eventos.html', {
            'eventos': eventos,
            'current_query': query
        })
    except Exception as e:
        print(f"Erro na view meus_eventos: {str(e)}")
        return render(request, 'core/meus_eventos.html', {
            'eventos': Evento.objects.none(),
            'current_query': request.GET.get('q')
        })

@login_required
def criar_evento(request):
    if request.user.tipo_usuario != 'organizador':
        return redirect('index')
    
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = request.user
            evento.save()
            form.save_m2m()  # Salva os campos ManyToMany como centros
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('meus_eventos')
    else:
        form = EventoForm()
    
    return render(request, 'core/evento_form.html', {
        'form': form,
        'action': 'Criar'
    })

@login_required
def editar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk, organizador=request.user)
    
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('meus_eventos')
    else:
        form = EventoForm(instance=evento)
    
    return render(request, 'core/evento_form.html', {
        'form': form,
        'evento': evento,
        'action': 'Editar'
    })

@login_required
def excluir_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk, organizador=request.user)
    
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento excluído com sucesso!')
        return redirect('meus_eventos')
    
    return render(request, 'core/evento_confirm_delete.html', {
        'evento': evento
    })

@login_required
def preferencias(request):
    user = request.user
    email_form = EmailChangeForm(user, request.POST or None, prefix='email') if request.method == 'POST' and 'update_email' in request.POST else EmailChangeForm(user, prefix='email')
    password_form = PasswordChangeForm(user, request.POST or None, prefix='password') if request.method == 'POST' and 'update_password' in request.POST else PasswordChangeForm(user, prefix='password')

    # Uniformizar os campos do PasswordChangeForm
    for field in password_form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    password_form.fields['old_password'].label = 'Senha atual'
    password_form.fields['old_password'].widget.attrs['placeholder'] = 'Digite sua senha atual'
    password_form.fields['new_password1'].label = 'Senha nova'
    password_form.fields['new_password1'].widget.attrs['placeholder'] = 'Digite sua nova senha'
    password_form.fields['new_password2'].label = 'Confirme a senha nova'
    password_form.fields['new_password2'].widget.attrs['placeholder'] = 'Confirme sua nova senha'
    
    # Uniformizar os campos do EmailChangeForm
    for field in email_form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    email_form.fields['password'].widget.attrs['placeholder'] = 'Digite sua senha para confirmar'
    email_form.fields['new_email'].widget.attrs['placeholder'] = 'Digite o novo e-mail'
    email_form.fields['confirm_email'].widget.attrs['placeholder'] = 'Confirme o novo e-mail'

    email_success = None
    password_success = None

    if request.method == 'POST':
        if 'update_email' in request.POST:
            if email_form.is_valid():
                email_form.save()
                email_success = 'E-mail atualizado com sucesso.'
                # Re-instantiate form to clear old data
                email_form = EmailChangeForm(user=request.user)
        elif 'update_password' in request.POST:
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                password_success = 'Senha alterada com sucesso.'
                # Re-instantiate form to clear old data
                password_form = PasswordChangeForm(user=request.user)

    return render(request, 'core/preferencias.html', {
        'user': user,
        'email_form': email_form,
        'password_form': password_form,
        'email_success': email_success,
        'password_success': password_success,
    })

@login_required
def meus_eventos_aluno(request):
    if request.user.tipo_usuario != 'aluno':
        return redirect('index')
    eventos = request.user.eventos_inscritos.all().order_by('-data_hora')
    return render(request, 'core/meus_eventos_aluno.html', {'eventos': eventos})

def eventos_list(request):
    try:
        eventos = Evento.objects.all()
        
        # Search by query
        query = request.GET.get('q')
        if query:
            eventos = eventos.filter(
                Q(titulo__icontains=query) |
                Q(descricao__icontains=query) |
                Q(local__icontains=query)
            )
        
        # Data filter
        data = request.GET.get('data')
        if data:
            today = timezone.now().date()
            if data == 'hoje':
                eventos = eventos.filter(data_hora__date=today)
            elif data == 'amanha':
                tomorrow = today + timezone.timedelta(days=1)
                eventos = eventos.filter(data_hora__date=tomorrow)
            elif data == 'semana':
                start_of_week = today - timezone.timedelta(days=today.weekday())
                end_of_week = start_of_week + timezone.timedelta(days=6)
                eventos = eventos.filter(data_hora__date__range=[start_of_week, end_of_week])
            elif data == 'mes':
                start_of_month = today.replace(day=1)
                if today.month == 12:
                    end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timezone.timedelta(days=1)
                else:
                    end_of_month = today.replace(month=today.month + 1, day=1) - timezone.timedelta(days=1)
                eventos = eventos.filter(data_hora__date__range=[start_of_month, end_of_month])
        
        # Data personalizada
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')
        if data_inicio and data_fim:
            eventos = eventos.filter(data_hora__date__range=[data_inicio, data_fim])
        
        # Preço filter
        preco = request.GET.get('preco')
        if preco:
            eventos = eventos.filter(preco=preco)
        
        # Tipo de evento filter
        tipo_evento = request.GET.get('tipo_evento')
        if tipo_evento:
            eventos = eventos.filter(tipo_evento=tipo_evento)
        
        # Centro filter - agora filtra por múltiplos centros
        centros = request.GET.getlist('centro')
        if centros:
            eventos = eventos.filter(centros__codigo__in=centros).distinct()
        
        # Local filter
        local = request.GET.get('local')
        if local:
            eventos = eventos.filter(lugar=local)
        
        # Horas complementares filter
        if request.GET.get('horas') == 'true':
            eventos = eventos.filter(horas_complementares=True)
        
        # Eventos encerrados filter
        if request.GET.get('encerrados') != 'true':
            # Se não estiver marcado, oculta eventos encerrados
            hoje = date.today()
            eventos = eventos.filter(data_hora__date__gte=hoje)
        
        # Order by
        ordenar = request.GET.get('ordenar')
        if ordenar:
            if ordenar == 'data_proxima':
                eventos = eventos.order_by('data_hora')
            elif ordenar == 'data_distante':
                eventos = eventos.order_by('-data_hora')
            elif ordenar == 'preco_menor':
                eventos = eventos.order_by('preco')
            elif ordenar == 'preco_maior':
                eventos = eventos.order_by('-preco')
            else:  # relevancia
                eventos = eventos.order_by('-criado_em')
        else:
            eventos = eventos.order_by('-criado_em')
        
        # Adiciona o status de inscrição para cada evento
        if request.user.is_authenticated:
            for evento in eventos:
                evento.esta_inscrito = evento.esta_inscrito(request.user)
        
        context = {
            'eventos': eventos,
            'centros': Centro.objects.all(),  # Adiciona todos os centros para o filtro
            'current_query': query,
            'current_data': data,
            'current_data_inicio': data_inicio,
            'current_data_fim': data_fim,
            'current_preco': preco,
            'current_tipo_evento': tipo_evento,
            'current_centros': centros,
            'current_local': local,
            'current_horas': request.GET.get('horas'),
            'current_encerrados': request.GET.get('encerrados'),
            'current_ordenar': ordenar
        }
        
        return render(request, 'core/eventos_list.html', context)
        
    except Exception as e:
        print(f"Erro na view eventos_list: {str(e)}")
        return render(request, 'core/eventos_list.html', {'eventos': Evento.objects.none()})

@api_view(['GET'])
def eventos_api(request):
    eventos = Evento.objects.all()
    serializer = EventoSerializer(eventos, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def centros_api(request):
    centros = Centro.objects.all()
    serializer = CentroSerializer(centros, many=True)
    return Response(serializer.data)

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            code = str(random.randint(100000, 999999))
            request.session['reset_email'] = email
            request.session['reset_code'] = code
            # Envie o código por e-mail
            send_mail(
                'Seu código de verificação',
                f'Seu código de verificação é: {code}',
                'no-reply@puconnect.com',
                [email],
                fail_silently=False,
            )
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'E-mail não encontrado.'})
    return JsonResponse({'success': False, 'error': 'Requisição inválida.'})

def password_reset_verify(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        if code == request.session.get('reset_code'):
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Código inválido.'})
    return JsonResponse({'success': False, 'error': 'Requisição inválida.'})

def password_reset_new(request):
    if request.method == 'POST':
        password1 = request.POST.get('new_password1')
        password2 = request.POST.get('new_password2')
        email = request.session.get('reset_email')
        if password1 != password2:
            return JsonResponse({'success': False, 'error': 'As senhas não coincidem.'})
        try:
            user = User.objects.get(email=email)
            user.set_password(password1)
            user.save()
            # Limpa sessão
            request.session.pop('reset_email', None)
            request.session.pop('reset_code', None)
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuário não encontrado.'})
    return JsonResponse({'success': False, 'error': 'Requisição inválida.'})

def register_modal(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'core.backends.MatriculaBackend'
            auth_login(request, user)
            return JsonResponse({'success': True})
        else:
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(e) for e in field_errors]
            return JsonResponse({'success': False, 'errors': errors})
    return JsonResponse({'success': False, 'errors': {'__all__': ['Método inválido.']}}, status=400)

def login_modal(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return JsonResponse({'success': True})
        else:
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(e) for e in field_errors]
            return JsonResponse({'success': False, 'errors': errors})
    return JsonResponse({'success': False, 'errors': {'__all__': ['Método inválido.']}}, status=400)

@login_required
def evento_detail(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    esta_inscrito = evento.esta_inscrito(request.user) if request.user.is_authenticated else False
    vagas_disponiveis = evento.vagas_disponiveis()
    
    context = {
        'evento': evento,
        'esta_inscrito': esta_inscrito,
        'vagas_disponiveis': vagas_disponiveis,
        'pode_editar': request.user.is_authenticated and (request.user == evento.organizador or request.user.is_staff),
    }
    return render(request, 'core/evento_detail.html', context)
 