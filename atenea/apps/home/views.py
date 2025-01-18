# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
import os
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import  redirect
from django.contrib import messages
from .models import DatosDemograficos


def home(request):
    context = {'segment': 'home'}
    html_template = loader.get_template('home/home-page.html')
    return HttpResponse(html_template.render(context,request))

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

@login_required
def lista_pacientes(request):
    print("aqui")
    pacientes = DatosDemograficos.objects.all()  # Obtiene todos los registros
    return render(request, 'home/tables.html', {'pacientes': pacientes})

@login_required
def registro_demografico(request):
    if request.method == 'POST':
        try:
            print("aqui 3")
            print(request.POST['nombres_apellidos'])
            datos = DatosDemograficos(
                nombres_apellidos=request.POST['nombres_apellidos'],
                tipo_documento=request.POST['tipo_documento'],
                numero_documento=request.POST['numero_documento'],
                fecha_nacimiento=request.POST['fecha_nacimiento'],
                edad=request.POST['edad'],
                estado_civil=request.POST['estado_civil'],
                escolaridad=request.POST['escolaridad'],
                ocupacion=request.POST['ocupacion'],
                eps=request.POST['eps'],
                lateralidad=request.POST['lateralidad'],
                direccion=request.POST['direccion'],
                telefono=request.POST['telefono'],
                nombre_acompanante=request.POST['nombre_acompanante'],
                parentesco=request.POST['parentesco'],
                telefono_acompanante=request.POST['telefono_acompanante'],
                grupo_sanguineo=request.POST['grupo_sanguineo'],
                religion=request.POST['religion'],
                fecha_evaluacion=request.POST['fecha_evaluacion'],
                hora_evaluacion=request.POST['hora_evaluacion'],
                evaluador=request.POST['evaluador']
            )
            datos.save()
            messages.success(request, 'Datos demográficos guardados exitosamente.')
            return redirect('lista_pacientes')  # Ajusta según tu URL
        except Exception as e:
            messages.error(request, f'Error al guardar los datos: {str(e)}')
    
    return render(request, 'sleepexams/pacientForm.html')  # Ajusta según tu template

@login_required(login_url="/login/")
def pages(request):
    print("prueba")
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

         # Genera una lista de posibles rutas en subcarpetas
        template_paths = [
            os.path.join(dirpath, load_template)
            for dirpath, _, filenames in os.walk(settings.TEMPLATES[0]['DIRS'][0])
            if load_template in filenames
        ]

        # Intenta cargar el primer template encontrado
        if template_paths:
            html_template = loader.get_template(template_paths[0])
        else:
            # Si no se encuentra el archivo, renderiza la página 404
            html_template = loader.get_template('home/page-404.html')

        return HttpResponse(html_template.render(context, request))

    except Exception:
        # Maneja cualquier otro error cargando una página 500
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

@login_required
def logout_view(request):
    logout(request)
    return redirect('login') 

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # Redirige a la página principal
        else:
            # Manejo de error de autenticación
            return render(request, 'home/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'home/login.html')