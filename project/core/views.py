from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from .forms import UserRegistrationForm, UserLoginForm, EventoForm, UserProfileForm, EmailChangeForm
from .models import Evento, Inscricao, UserProfile
from django.contrib.auth.forms import PasswordChangeForm
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import EventoSerializer
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import JsonResponse
import random
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.urls import reverse

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
    return redirect('index')

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
    
    eventos = Evento.objects.filter(organizador=request.user).order_by('-data_hora')
    return render(request, 'core/meus_eventos.html', {
        'eventos': eventos
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
    password_form.fields['new_password1'].label = 'Senha nova'
    password_form.fields['new_password2'].label = 'Confirme a senha nova'

    email_success = None
    password_success = None

    if request.method == 'POST':
        if 'update_email' in request.POST:
            if email_form.is_valid():
                email_form.save()
                email_success = 'E-mail atualizado com sucesso.'
        elif 'update_password' in request.POST:
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                password_success = 'Senha alterada com sucesso.'

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
    eventos = Evento.objects.all()
    
    # Search by query
    query = request.GET.get('q')
    if query:
        eventos = eventos.filter(
            Q(titulo__icontains=query) |
            Q(descricao__icontains=query) |
            Q(local__icontains=query)
        )
    
    # Additional keyword search
    keyword = request.GET.get('keyword')
    if keyword:
        eventos = eventos.filter(
            Q(titulo__icontains=keyword) |
            Q(descricao__icontains=keyword) |
            Q(local__icontains=keyword)
        )
    
    # Period filter
    period = request.GET.get('period')
    if period:
        today = timezone.now().date()
        if period == 'today':
            eventos = eventos.filter(data_hora__date=today)
        elif period == 'week':
            start_of_week = today - timezone.timedelta(days=today.weekday())
            end_of_week = start_of_week + timezone.timedelta(days=6)
            eventos = eventos.filter(data_hora__date__range=[start_of_week, end_of_week])
        elif period == 'month':
            start_of_month = today.replace(day=1)
            if today.month == 12:
                end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timezone.timedelta(days=1)
            else:
                end_of_month = today.replace(month=today.month + 1, day=1) - timezone.timedelta(days=1)
            eventos = eventos.filter(data_hora__date__range=[start_of_month, end_of_month])
    
    # My events filter
    if request.GET.get('my_events') and request.user.is_authenticated:
        eventos = eventos.filter(inscritos=request.user)
    
    # Order by date
    eventos = eventos.order_by('data_hora')
    
    return render(request, 'core/eventos_list.html', {
        'eventos': eventos,
        'current_query': query,
        'current_keyword': keyword,
        'current_period': period,
        'current_my_events': request.GET.get('my_events')
    })

@api_view(['GET'])
def eventos_api(request):
    eventos = Evento.objects.all()
    serializer = EventoSerializer(eventos, many=True, context={'request': request})
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
 