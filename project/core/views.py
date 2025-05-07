from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')

def login(request):
    return render(request, 'core/login.html') 

def inscricoes(request):
    return render(request, 'core/inscricoes.html')

 