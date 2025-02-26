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
from .models import DatosDemograficos, Proyecto, Examen, Visita, VisitaExamen
from .forms import  ProyectoForm,RegistroDemograficoForm,AnamnesisForm
import json

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
                # Datos obligatorios
                primer_nombre=request.POST['primer_nombre'],
                primer_apellido=request.POST['primer_apellido'],
                numero_documento=request.POST['numero_documento'],
                fecha_nacimiento=request.POST['fecha_nacimiento'],
                edad=24,
                rh=request.POST['grupo_sanguineo'],
                correo=request.POST['correo'],
                celular=request.POST['celular'],

                # Datos opcionales (se usa `.get()` para evitar errores si faltan)
                segundo_nombre=request.POST.get('segundo_nombre', ''),
                segundo_apellido=request.POST.get('segundo_apellido', ''),
                lugar_nacimiento=request.POST.get('lugar_nacimiento', ''),
                genero=request.POST.get('genero', ''),
                escolaridad=request.POST.get('escolaridad', ''),
                lateralidad=request.POST.get('lateralidad', ''),
                estado_civil=request.POST.get('estado_civil', ''),
                ocupacion=request.POST.get('ocupacion', ''),
                eps=request.POST.get('eps', ''),
                direccion_residencia=request.POST.get('direccion_residencia', ''),
                municipio_residencia=request.POST.get('municipio_residencia', ''),
                departamento_residencia=request.POST.get('departamento_residencia', ''),
                pais_residencia=request.POST.get('pais_residencia', ''),
                grupo_sanguineo=request.POST.get('grupo_sanguineo', ''),
                religion=request.POST.get('religion', ''),
                numero_hijos=request.POST.get('numero_hijos', 0),

                # Datos del Acompañante
                nombre_acompanante=request.POST.get('nombre_acompanante', ''),
                relacion_acompanante=request.POST.get('relacion_acompanante', ''),
                correo_acompanante=request.POST.get('correo_acompanante', ''),
                telefono_acompanante=request.POST.get('telefono_acompanante', '')
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
        print("aqui")
        form = RegistroDemograficoForm(request.POST, instance=paciente)  # Cargar los datos del paciente
        if form.is_valid():
            form.save()  # Guardar los cambios
            pacientes = DatosDemograficos.objects.all()
            messages.success(request, 'Datos demográficos editados exitosamente.')
    
            return render(request, 'home/tables.html', {'pacientes': pacientes})
    
        else:
            messages.error(request, '❌ Error en el formulario. Verifica los campos.')
            print(form.errors)  # Para depuración en la consola
        
  # Redirigir a una página de detalle del paciente
    if request.method == 'GET':
        form = RegistroDemograficoForm(instance=paciente)  # Cargar el formulario con los datos del paciente
        return render(request, 'sleepexams/editPacientForm.html', {'form': form})

@login_required
def detalle_paciente(request, paciente_id):
    proyectos = Proyecto.objects.all()
    paciente = get_object_or_404(DatosDemograficos, numero_documento=paciente_id)
    # Obtener los proyectos en los que el paciente ya está asignado
    proyectos_asociados = paciente.proyectos.all()

    # Obtener proyectos disponibles para asignación (excluye los que ya tiene)
    proyectos_disponibles = Proyecto.objects.exclude(id__in=proyectos_asociados.values_list('id', flat=True))
    
    if request.method == "POST":
        proyecto_id = request.POST.get("proyecto_id")
        pacientes_ids = request.POST.getlist("paciente_id")  # Lista de IDs seleccionados

        proyecto = Proyecto.objects.get(id=proyecto_id)
        proyecto.pacientes.set(pacientes_ids)  # Asigna los pacientes al proyecto
        proyecto.save()
        
    return render(request, 'sleepexams/pacient.html', {'paciente': paciente,'proyectos':proyectos,'proyectos_asociados': proyectos_asociados,
        'proyectos_disponibles': proyectos_disponibles})

#proyectos
@login_required
def proyectos(request):
    proyectos = Proyecto.objects.all()
    examenes = Examen.objects.all()
    visitas = Visita.objects.all()
    visitaexamen = VisitaExamen.objects.all()
    
    # Crear un diccionario para almacenar las visitas y exámenes por proyecto
    proyecto_data = {}
    for proyecto in proyectos:
        visitas_proyecto = visitas.filter(proyecto=proyecto)
        visitas_info = []
        for visita in visitas_proyecto:
            examenes_visita = visitaexamen.filter(visita=visita)
            visitas_info.append({
                'nombre': visita.nombre,
                'fecha': visita.fecha,
                'observaciones': visita.observaciones,
                'examenes': [ve.examen for ve in examenes_visita]
            })
        proyecto_data[proyecto.id] = visitas_info
    
    context = {
        'proyectos': proyectos,
        'examenes': examenes,
        'visitas': visitas,
        'visitaexamen': visitaexamen,
        'proyecto_data': proyecto_data
    }
    
    if request.method == 'POST':
        proyecto_form = ProyectoForm(request.POST)
        if proyecto_form.is_valid():
            proyecto_form.save()
            messages.success(request, 'Proyecto creado correctamente.')
    
    return render(request, 'home/proyectos.html', context)

@login_required
def eliminar_proyecto(request, id):
    proyectos = Proyecto.objects.all()
    if request.method == 'POST':
        proyecto = get_object_or_404(Proyecto, id=id)  # Asegúrate de que Proyecto es el nombre del modelo de tus proyectos
        proyecto.delete()
        messages.success(request, f"El proyecto con ID {id} ha sido eliminado.")
        return render(request, 'home/proyectos.html',{'proyectos': proyectos})  # Redirige a la lista de proyectos, por ejemplo
    else:
        messages.error(request, "Método no permitido.")
        return render(request, 'home/proyectos.html',{'proyectos': proyectos})  # Redirige a la lista de proyectos si no es un POST

@login_required
#visitas
def agregar_visita(request):
    proyectos = Proyecto.objects.all()
    examenes = Examen.objects.all()
    visitas = Visita.objects.all()
    visitaexamen = VisitaExamen.objects.all()
    
    # Crear un diccionario para almacenar las visitas y exámenes por proyecto
    proyecto_data = {}
    for proyecto in proyectos:
        visitas_proyecto = visitas.filter(proyecto=proyecto)
        visitas_info = []
        for visita in visitas_proyecto:
            examenes_visita = visitaexamen.filter(visita=visita)
            visitas_info.append({
                'nombre': visita.nombre,
                'fecha': visita.fecha,
                'observaciones': visita.observaciones,
                'examenes': [ve.examen for ve in examenes_visita]
            })
        proyecto_data[proyecto.id] = visitas_info
    
    context = {
        'proyectos': proyectos,
        'examenes': examenes,
        'visitas': visitas,
        'visitaexamen': visitaexamen,
        'proyecto_data': proyecto_data
    }
   
    if request.method == 'POST':
        proyecto_id = request.POST.get('proyecto_id')
        nombres = request.POST.getlist('nombre_visita[]')  # Varias visitas
        fechas = request.POST.getlist('fecha_visita[]')
        observaciones_list = request.POST.getlist('observaciones[]')

        for i in range(len(nombres)):
            visita = Visita.objects.create(
                proyecto_id=proyecto_id,
                nombre=nombres[i],
                fecha=fechas[i],
                observaciones=observaciones_list[i]
            )

            examenes_ids = request.POST.getlist('examenes[]') 

            # Guardar cada examen seleccionado en la BD
            for examen_id in examenes_ids:
                VisitaExamen.objects.create(
                    visita=visita,
                    examen_id=examen_id,  # Más eficiente usar .create() con el ID directo
                    resultado={}
                )

    return render(request, 'home/proyectos.html',context)

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

def examen_anamnesis(request):
    form=AnamnesisForm()
    preguntas_sintomas = [
        "dificultad_conciliacion",
        "dificultad_mantenimiento",
        "apnea",
        "ronquido",
        "somnolencia_diurna",
        "hipersomnolencia"
    ]
    if request.method == 'POST':
        form = AnamnesisForm(request.POST)
        if form.is_valid():
            messages.success(request, '✅ Examen de Anamnesis guardado correctamente.')
            return redirect('listado_examenes')  # Cambia a la vista correcta
        else:
            messages.error(request, '❌ Error en el formulario.')
    else:
        form = AnamnesisForm()

    return render(request, 'sleepexams/anamnesisTest.html', {'form': form,'preguntas_sintomas': preguntas_sintomas})