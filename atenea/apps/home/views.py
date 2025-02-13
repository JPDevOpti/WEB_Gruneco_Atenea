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
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect
from django.contrib import messages
from apps.home import models,forms
from .models import DatosDemograficos, Proyecto, Visita
from .forms import RegistroDemograficoForm, ProyectoForm

#vista principal
def home(request):
    context = {'segment': 'home'}
    html_template = loader.get_template('home/home-page.html')
    return HttpResponse(html_template.render(context, request))

#dasboard
@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

#pacientes
@login_required
def lista_pacientes(request):
    pacientes = DatosDemograficos.objects.all()
    return render(request, 'home/tables.html', {'pacientes': pacientes})

@login_required
def registro_demografico(request):
    if request.method == 'POST':
        try:
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
                grupo_sanguineo=request.POST['grupo_sanguineo'],
                religion=request.POST['religion'],
            )
            datos.save()
            messages.success(request, 'Datos demográficos guardados exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al guardar los datos: {str(e)}')

        pacientes = DatosDemograficos.objects.all()
        return render(request, 'home/tables.html', {'pacientes': pacientes})

    if request.method == 'GET':
        return render(request, 'sleepexams/pacientForm.html')

@login_required
def eliminar_paciente(request, numero_documento):
    if request.method == 'POST':
        paciente = get_object_or_404(DatosDemograficos, numero_documento=numero_documento)
        paciente.delete()
        messages.success(request, f"El paciente con documento {numero_documento} ha sido eliminado.")
        return redirect('tables.html')
    else:
        messages.error(request, "Método no permitido.")
        return redirect('tables.html')
@login_required
def editar_paciente(request, numero_documento):
    paciente = get_object_or_404(DatosDemograficos, numero_documento=numero_documento)  # Obtener el paciente por su ID
    
    if request.method == 'POST':
        form = RegistroDemograficoForm(request.POST, instance=paciente)  # Cargar los datos del paciente
        if form.is_valid():
            form.save()  # Guardar los cambios
            pacientes = DatosDemograficos.objects.all()
            messages.success(request, 'Datos demográficos editados exitosamente.')
    
            return render(request, 'home/tables.html', {'pacientes': pacientes})
        
  # Redirigir a una página de detalle del paciente
    if request.method == 'GET':
        form = RegistroDemograficoForm(instance=paciente)  # Cargar el formulario con los datos del paciente
        print("Fecha de Nacimiento:", paciente.fecha_nacimiento)
        return render(request, 'sleepexams/editPacientForm.html', {'form': form})

@login_required
def detalle_paciente(request, paciente_id):
    proyectos = Proyecto.objects.all()
    paciente = get_object_or_404(DatosDemograficos, numero_documento=paciente_id)
    return render(request, 'sleepexams/pacient.html', {'paciente': paciente,'proyectos':proyectos})

#proyectos
@login_required
def proyectos(request):
    proyectos = Proyecto.objects.all()
    if request.method == 'POST':
        proyecto_form = ProyectoForm(request.POST)
        if proyecto_form.is_valid():
            proyecto_form.save()
            messages.success(request, 'Proyecto creado correctamente.')
 
    return render(request, 'home/proyectos.html',{'proyectos': proyectos})

def agregar_visita(request):
    proyectos = Proyecto.objects.all()
    if request.method == "POST":
        nombre = request.POST.get("proyectoNombre")
        fecha_visita = request.POST.get("fecha_visita")
        descripcion = request.POST.get("descripcion")
        
        proyecto = get_object_or_404(Proyecto, nombre=nombre)
        Visita.objects.create(proyecto=proyecto, fecha_visita=fecha_visita, descripcion=descripcion)

        messages.success(request, "Visita agregada correctamente")
    return render(request, 'home/proyectos.html',{'proyectos': proyectos})

@login_required(login_url="/login/")
def pages(request):
    print("prueba paginas")
    context = {}

    try:
        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        template_paths = [
            os.path.join(dirpath, load_template)
            for dirpath, _, filenames in os.walk(settings.TEMPLATES[0]['DIRS'][0])
            if load_template in filenames
        ]

        if template_paths:
            html_template = loader.get_template(template_paths[0])
        else:
            html_template = loader.get_template('home/page-404.html')

        return HttpResponse(html_template.render(context, request))

    except Exception:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

#Ingreso y Salida
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
            return redirect('index')
        else:
            return render(request, 'home/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'home/login.html')

def consulta_view(request):
    return render(request, 'home/consulta.html')
