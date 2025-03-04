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
from .models import DatosDemograficos, Proyecto, Examen, Visita, VisitaExamen,ResultadoExamen
from .forms import  ProyectoForm,RegistroDemograficoForm,AnamnesisForm
import json
from reportlab.pdfgen import canvas
from io import BytesIO

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

@login_required(login_url="/login/")
def estadisticas(request):
    context = {'segment': 'estadisticas'}
    html_template = loader.get_template('home/stadistic.html')
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
                edad=request.POST['edad'],
                correo=request.POST['correo'],
                celular=request.POST['celular'],
                regimen=request.POST['regimen'],
                tipo_documento=request.POST['tipo_documento'],

                # Datos opcionales (se usa `.get()` para evitar errores si faltan)
                segundo_nombre=request.POST.get('segundo_nombre', ''),
                segundo_apellido=request.POST.get('segundo_apellido', ''),
                genero=request.POST.get('genero', ''),
                escolaridad=request.POST.get('escolaridad', ''),
                lateralidad=request.POST.get('lateralidad', ''),
                estado_civil=request.POST.get('estado_civil', ''),
                ocupacion=request.POST.get('ocupacion', ''),
                eps=request.POST.get('eps', ''),
                
                direccion=request.POST.get('direccion', ''),
                municipio_residencia=request.POST.get('municipio_residencia', ''),
                departamento_residencia=request.POST.get('departamento_residencia', ''),
                pais_residencia=request.POST.get('pais_residencia', ''),
                
                municipio_nacimiento = request.POST.get('municipio_nacimiento', ''),
                departamento_nacimiento = request.POST.get('departamento_nacimiento', ''),
                pais_nacimiento =request.POST.get('pais_nacimiento', ''),
                
                grupo_sanguineo=request.POST.get('grupo_sanguineo', ''),
                religion=request.POST.get('religion', ''),
            
            )
            datos.save()
            messages.success(request, 'Datos demográficos guardados exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al guardar los datos: {str(e)}')

        pacientes = DatosDemograficos.objects.all()
        return redirect('tables.html')
    
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
            messages.error(request, f'❌ Error en el formulario. Verifica los campos. {str(form.errors)}')
            return render(request, 'sleepexams/editPacientForm.html', {'form': form})
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
    
    # Obtener todas las visitas asociadas al paciente
    visitas = Visita.objects.filter(proyecto__in=proyectos_asociados)

    # Obtener todos los exámenes realizados o pendientes en esas visitas
    visita_examenes = VisitaExamen.objects.filter(visita__in=visitas)

    # Crear una lista de IDs de exámenes realizados
    examenes_realizados = []
    for visita_examen in visita_examenes:
        resultado_examen = ResultadoExamen.objects.filter(
            visita_examen=visita_examen,
            paciente=paciente
        ).first()
        if resultado_examen and resultado_examen.resultado:
            examenes_realizados.append(visita_examen.id)
    
        

    if request.method == "POST":
        proyecto_id = request.POST.get("proyecto_id")
        pacientes_ids = request.POST.get("paciente_id")  # Lista de IDs seleccionados

        proyecto = Proyecto.objects.get(id=proyecto_id)
        proyecto.pacientes.add(pacientes_ids)  # Asigna los pacientes al proyecto
        proyecto.save()
        
    return render(request, 'sleepexams/pacient.html', {'paciente': paciente,'proyectos':proyectos,'proyectos_asociados': proyectos_asociados,
        'proyectos_disponibles': proyectos_disponibles,'examenes_realizados': examenes_realizados,})

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
                )
            # Redirigir a la página de proyectos
        return redirect('proyectos')

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

#examenes
def realizar_examen(request, visita_id, examen_id, paciente_id):

    # Diccionario de plantillas según el examen
    exam_templates = {
        3: "sleepexams/General_ExamenFísico.html",
        4: "sleepexams/General_RevisiónSistemas.html",
        5: "sleepexams/General_Antecedentes.html",
    }

    template = exam_templates.get(examen_id, "sleepexams/anamnesisTest.html")  

    return render(request, template, {'visita_examen': visita_id, 'paciente_id':paciente_id})

def guardar_examen_general_revisionsistemas(request):
    
    if request.method == 'POST':
        # Obtener los datos del formulario
        datos_formulario = {
            "General": {
                "sintoma_general": request.POST.get('sintoma_general'),
                "detalle_sintoma_general": request.POST.get('detalle_sintoma_general'),
                "tiempo_sintoma_general": request.POST.get('tiempo_sintoma_general'),
                "caracteristicas_sintoma_general": request.POST.get('caracteristicas_sintoma_general'),
            },
            "Cabeza y cuello": {
                "sintoma_cabeza_cuello": request.POST.get('sintoma_cabeza_cuello'),
                "detalle_sintoma_cabeza_cuello": request.POST.get('detalle_sintoma_cabeza_cuello'),
                "tiempo_sintoma_cabeza_cuello": request.POST.get('tiempo_sintoma_cabeza_cuello'),
                "caracteristicas_sintoma_cabeza_cuello": request.POST.get('caracteristicas_sintoma_cabeza_cuello'),
            },
            "Cardiopulmonar": {
                "sintoma_cardiopulmonar": request.POST.get('sintoma_cardiopulmonar'),
                "detalle_sintoma_cardiopulmonar": request.POST.get('detalle_sintoma_cardiopulmonar'),
                "tiempo_sintoma_cardiopulmonar": request.POST.get('tiempo_sintoma_cardiopulmonar'),
                "caracteristicas_sintoma_cardiopulmonar": request.POST.get('caracteristicas_sintoma_cardiopulmonar'),
            },
            "Gastrointestinal": {
                "sintoma_gastrointestinal": request.POST.get('sintoma_gastrointestinal'),
                "detalle_sintoma_gastrointestinal": request.POST.get('detalle_sintoma_gastrointestinal'),
                "tiempo_sintoma_gastrointestinal": request.POST.get('tiempo_sintoma_gastrointestinal'),
                "caracteristicas_sintoma_gastrointestinal": request.POST.get('caracteristicas_sintoma_gastrointestinal'),
            },
            "Genitourinario": {
                "sintoma_genitourinario": request.POST.get('sintoma_genitourinario'),
                "detalle_sintoma_genitourinario": request.POST.get('detalle_sintoma_genitourinario'),
                "tiempo_sintoma_genitourinario": request.POST.get('tiempo_sintoma_genitourinario'),
                "caracteristicas_sintoma_genitourinario": request.POST.get('caracteristicas_sintoma_genitourinario'),
            },
            "Vascular periférico": {
                "sintoma_vascular_periferico": request.POST.get('sintoma_vascular_periferico'),
                "detalle_sintoma_vascular_periferico": request.POST.get('detalle_sintoma_vascular_periferico'),
                "tiempo_sintoma_vascular_periferico": request.POST.get('tiempo_sintoma_vascular_periferico'),
                "caracteristicas_sintoma_vascular_periferico": request.POST.get('caracteristicas_sintoma_vascular_periferico'),
            },
            "Osteomuscular": {
                "sintoma_osteomuscular": request.POST.get('sintoma_osteomuscular'),
                "detalle_sintoma_osteomuscular": request.POST.get('detalle_sintoma_osteomuscular'),
                "tiempo_sintoma_osteomuscular": request.POST.get('tiempo_sintoma_osteomuscular'),
                "caracteristicas_sintoma_osteomuscular": request.POST.get('caracteristicas_sintoma_osteomuscular'),
            },
            "Piel y Faneras": {
                "sintoma_piel_faneras": request.POST.get('sintoma_piel_faneras'),
                "detalle_sintoma_piel_faneras": request.POST.get('detalle_sintoma_piel_faneras'),
                "tiempo_sintoma_piel_faneras": request.POST.get('tiempo_sintoma_piel_faneras'),
                "caracteristicas_sintoma_piel_faneras": request.POST.get('caracteristicas_sintoma_piel_faneras'),
            },
            "Otros": {
                "sintoma_otros": request.POST.get('sintoma_otros'),
                "detalle_sintoma_otros": request.POST.get('detalle_sintoma_otros'),
                "tiempo_sintoma_otros": request.POST.get('tiempo_sintoma_otros'),
                "caracteristicas_sintoma_otros": request.POST.get('caracteristicas_sintoma_otros'),
            },
        }

        # Obtener la visita y el examen correspondiente
        visita_examen_id = request.POST.get('visita_examen')  # Asegúrate de pasar el ID de la visita en el formulario
        paciente_id = request.POST.get('paciente_id') 
        
        paciente = get_object_or_404(DatosDemograficos, id=paciente_id)
        documento_paciente = paciente.numero_documento
        print('documento_paciente')

        # Obtener o crear el VisitaExamen correspondiente
        visita_examen, created = VisitaExamen.objects.get_or_create(
            id=visita_examen_id
        )
        
        # Crear o actualizar el registro de ResultadoExamen
        resultado_examen, created = ResultadoExamen.objects.get_or_create(
            visita_examen=visita_examen,
            paciente=paciente,  # Usar el objeto Paciente, no el ID
            defaults={'resultado': datos_formulario}
        )

        if not created:
            resultado_examen.resultado = datos_formulario
            resultado_examen.save()

        return redirect(reverse('detalle_paciente', args=[int(documento_paciente)])) # Redirigir a una página de éxito

def guardar_examen_fisico(request):
    if request.method == 'POST':
        print('fisico')
        # Obtener los datos del formulario
        datos_formulario_fisico = {
            "Signos Vitales": {
                "talla": request.POST.get('talla'),
                "peso": request.POST.get('peso'),
                "temperatura": request.POST.get('temperatura'),
                "frecuencia_cardiaca": request.POST.get('frecuencia_cardiaca'),
                "frecuencia_respiratoria": request.POST.get('frecuencia_respiratoria'),
                "presion_arterial_sistolica": request.POST.get('presion_arterial_sistolica'),
                "presion_arterial_diastolica": request.POST.get('presion_arterial_diastolica'),
                "perimetro_cefalico": request.POST.get('perimetro_cefalico'),
            },
            "Cabeza y Cuello": {
                "cuero_cabelludo": request.POST.get('cuero_cabelludo'),
                "observaciones_cuero_cabelludo": request.POST.get('observaciones_cuero_cabelludo'),
                "oidos": request.POST.get('oidos'),
                "observaciones_oidos": request.POST.get('observaciones_oidos'),
                "nariz": request.POST.get('nariz'),
                "observaciones_nariz": request.POST.get('observaciones_nariz'),
                "cuello": request.POST.get('cuello'),
                "observaciones_cuello": request.POST.get('observaciones_cuello'),
                "otros_hallazgos_cabeza_cuello": request.POST.get('otros_hallazgos_cabeza_cuello'),
            },
            "Tórax / Respiratorio / Cardiovascular": {
                "forma_torax": request.POST.get('forma_torax'),
                "observaciones_forma_torax": request.POST.get('observaciones_forma_torax'),
                "murmullo_vesicular": request.POST.get('murmullo_vesicular'),
                "observaciones_murmullo_vesicular": request.POST.get('observaciones_murmullo_vesicular'),
                "ruidos_sobreagregados": request.POST.get('ruidos_sobreagregados'),
                "observaciones_ruidos_sobreagregados": request.POST.get('observaciones_ruidos_sobreagregados'),
                "ruidos_cardiacos": request.POST.get('ruidos_cardiacos'),
                "observaciones_ruidos_cardiacos": request.POST.get('observaciones_ruidos_cardiacos'),
            },
            "Abdomen": {
                "peristaltismo": request.POST.get('peristaltismo'),
                "pared_abdominal": request.POST.get('pared_abdominal'),
                "masas": request.POST.get('masas'),
                "megalias": request.POST.get('megalias'),
                "observaciones_abdomen": request.POST.get('observaciones_abdomen'),
            },
            "Osteomuscular": {
                "curvatura_cervical": request.POST.get('curvatura_cervical'),
                "curvatura_toracica": request.POST.get('curvatura_toracica'),
                "curvatura_lumbar": request.POST.get('curvatura_lumbar'),
                "arcos_movimiento_superiores": request.POST.get('arcos_movimiento_superiores'),
                "arcos_movimiento_inferiores": request.POST.get('arcos_movimiento_inferiores'),
                "asimetrias_inferiores": request.POST.get('asimetrias_inferiores'),
                "asimetrias_superiores": request.POST.get('asimetrias_superiores'),
                "observaciones_osteomuscular": request.POST.get('observaciones_osteomuscular'),
            },
            "Piel y Anexos": {
                "maculas": request.POST.get('maculas'),
                "papulas": request.POST.get('papulas'),
                "vesiculas": request.POST.get('vesiculas'),
                "pustulas": request.POST.get('pustulas'),
                "fisuras": request.POST.get('fisuras'),
                "escaras": request.POST.get('escaras'),
                "petequias": request.POST.get('petequias'),
                "equimosis": request.POST.get('equimosis'),
                "ulceras": request.POST.get('ulceras'),
                "observaciones_piel": request.POST.get('observaciones_piel'),
            },
        }

        # Obtener la visita y el examen correspondiente
        visita_examen_id = request.POST.get('visita_examen')  # Asegúrate de pasar el ID de la visita en el formulario
        paciente_id = request.POST.get('paciente_id') 
        paciente = get_object_or_404(DatosDemograficos, id=paciente_id)
        documento_paciente = paciente.numero_documento
        
        # Obtener o crear el VisitaExamen correspondiente
        visita_examen, created = VisitaExamen.objects.get_or_create(
            id=visita_examen_id
        )
        
        # Crear o actualizar el registro de ResultadoExamen
        resultado_examen, created = ResultadoExamen.objects.get_or_create(
            visita_examen=visita_examen,
            paciente=paciente,  # Usar el objeto Paciente, no el ID
            defaults={'resultado': datos_formulario_fisico}
        )

        if not created:
            resultado_examen.resultado = datos_formulario_fisico
            resultado_examen.save()

        return redirect(reverse('detalle_paciente', args=[int(documento_paciente)])) # Redirigir a una página de éxito
 
def guardar_examen_antecedentes(request):
    if request.method == 'POST':
        print('aqui antecendtes')
        # Obtener los datos del formulario para antecedentes
        datos_formulario_antecedentes = {
            "Antecedentes Patológicos": {
                "antecedente_patologico": request.POST.get('antecedente_patologico'),
                "tipo_patologia": request.POST.get('tipo_patologia'),
                "fecha_inicio_patologia": request.POST.get('fecha_inicio_patologia'),
                "tratamiento_patologico": request.POST.get('tratamiento_patologico'),
                "detalle_tratamiento_patologico": request.POST.get('detalle_tratamiento_patologico'),
                "complicaciones_patologico": request.POST.get('complicaciones_patologico'),
                "detalle_complicaciones_patologico": request.POST.get('detalle_complicaciones_patologico'),
                "activo_patologico": request.POST.get('activo_patologico'),
                "fecha_finalizacion_patologico": request.POST.get('fecha_finalizacion_patologico'),
                "observaciones_patologico": request.POST.get('observaciones_patologico'),
            },
            "Antecedentes Quirúrgicos": {
                "antecedente_quirurgico": request.POST.get('antecedente_quirurgico'),
                "descripcion_quirurgico": request.POST.get('descripcion_quirurgico'),
                "fecha_inicio_quirurgico": request.POST.get('fecha_inicio_quirurgico'),
                "tratamiento_quirurgico": request.POST.get('tratamiento_quirurgico'),
                "detalle_tratamiento_quirurgico": request.POST.get('detalle_tratamiento_quirurgico'),
                "complicaciones_quirurgico": request.POST.get('complicaciones_quirurgico'),
                "detalle_complicaciones_quirurgico": request.POST.get('detalle_complicaciones_quirurgico'),
                "activo_quirurgico": request.POST.get('activo_quirurgico'),
                "fecha_finalizacion_quirurgico": request.POST.get('fecha_finalizacion_quirurgico'),
                "observaciones_quirurgico": request.POST.get('observaciones_quirurgico'),
            },
            "Antecedentes Farmacológicos": {
                "antecedente_farmacologico": request.POST.get('antecedente_farmacologico'),
                "descripcion_farmacologico": request.POST.get('descripcion_farmacologico'),
                "fecha_inicio_farmacologico": request.POST.get('fecha_inicio_farmacologico'),
                "tratamiento_farmacologico": request.POST.get('tratamiento_farmacologico'),
                "detalle_tratamiento_farmacologico": request.POST.get('detalle_tratamiento_farmacologico'),
                "complicaciones_farmacologico": request.POST.get('complicaciones_farmacologico'),
                "detalle_complicaciones_farmacologico": request.POST.get('detalle_complicaciones_farmacologico'),
                "activo_farmacologico": request.POST.get('activo_farmacologico'),
                "fecha_finalizacion_farmacologico": request.POST.get('fecha_finalizacion_farmacologico'),
                "observaciones_farmacologico": request.POST.get('observaciones_farmacologico'),
            },
            "Antecedentes Traumáticos": {
                "antecedente_traumatico": request.POST.get('antecedente_traumatico'),
                "descripcion_traumatico": request.POST.get('descripcion_traumatico'),
                "fecha_inicio_traumatico": request.POST.get('fecha_inicio_traumatico'),
                "tratamiento_traumatico": request.POST.get('tratamiento_traumatico'),
                "detalle_tratamiento_traumatico": request.POST.get('detalle_tratamiento_traumatico'),
                "complicaciones_traumatico": request.POST.get('complicaciones_traumatico'),
                "detalle_complicaciones_traumatico": request.POST.get('detalle_complicaciones_traumatico'),
                "activo_traumatico": request.POST.get('activo_traumatico'),
                "fecha_finalizacion_traumatico": request.POST.get('fecha_finalizacion_traumatico'),
                "observaciones_traumatico": request.POST.get('observaciones_traumatico'),
            },
            "Antecedentes Alérgicos": {
                "antecedente_alergico": request.POST.get('antecedente_alergico'),
                "descripcion_alergico": request.POST.get('descripcion_alergico'),
                "fecha_inicio_alergico": request.POST.get('fecha_inicio_alergico'),
                "tratamiento_alergico": request.POST.get('tratamiento_alergico'),
                "detalle_tratamiento_alergico": request.POST.get('detalle_tratamiento_alergico'),
                "complicaciones_alergico": request.POST.get('complicaciones_alergico'),
                "detalle_complicaciones_alergico": request.POST.get('detalle_complicaciones_alergico'),
                "activo_alergico": request.POST.get('activo_alergico'),
                "fecha_finalizacion_alergico": request.POST.get('fecha_finalizacion_alergico'),
                "observaciones_alergico": request.POST.get('observaciones_alergico'),
            },
            "Antecedentes Tóxicos": {
                "antecedente_toxico": request.POST.get('antecedente_toxico'),
                "tipo_toxico": request.POST.get('tipo_toxico'),
                "fecha_inicio_toxico": request.POST.get('fecha_inicio_toxico'),
                "tratamiento_toxico": request.POST.get('tratamiento_toxico'),
                "detalle_tratamiento_toxico": request.POST.get('detalle_tratamiento_toxico'),
                "complicaciones_toxico": request.POST.get('complicaciones_toxico'),
                "detalle_complicaciones_toxico": request.POST.get('detalle_complicaciones_toxico'),
                "activo_toxico": request.POST.get('activo_toxico'),
                "fecha_finalizacion_toxico": request.POST.get('fecha_finalizacion_toxico'),
                "observaciones_toxico": request.POST.get('observaciones_toxico'),
            },
            "Antecedentes Epidemiológicos": {
                "antecedente_epidemiologico": request.POST.get('antecedente_epidemiologico'),
                "descripcion_epidemiologico": request.POST.get('descripcion_epidemiologico'),
                "fecha_inicio_epidemiologico": request.POST.get('fecha_inicio_epidemiologico'),
                "tratamiento_epidemiologico": request.POST.get('tratamiento_epidemiologico'),
                "detalle_tratamiento_epidemiologico": request.POST.get('detalle_tratamiento_epidemiologico'),
                "complicaciones_epidemiologico": request.POST.get('complicaciones_epidemiologico'),
                "detalle_complicaciones_epidemiologico": request.POST.get('detalle_complicaciones_epidemiologico'),
                "activo_epidemiologico": request.POST.get('activo_epidemiologico'),
                "fecha_finalizacion_epidemiologico": request.POST.get('fecha_finalizacion_epidemiologico'),
                "observaciones_epidemiologico": request.POST.get('observaciones_epidemiologico'),
            },
            "Antecedentes Gineco-Obstétricos": {
                "antecedente_gineco_obstetrico": request.POST.get('antecedente_gineco_obstetrico'),
                "menarquia": request.POST.get('menarquia'),
                "edad_menarquia": request.POST.get('edad_menarquia'),
                "menopausia": request.POST.get('menopausia'),
                "edad_menopausia": request.POST.get('edad_menopausia'),
                "gravidez": request.POST.get('gravidez'),
                "abortos": request.POST.get('abortos'),
                "hijos_vivos": request.POST.get('hijos_vivos'),
                "metodo_planificacion": request.POST.get('metodo_planificacion'),
                "metodo_planificacion_detalle": request.POST.get('metodo_planificacion_detalle'),
                "dosis_planificacion": request.POST.get('dosis_planificacion'),
                "adherencia_planificacion": request.POST.get('adherencia_planificacion'),
                "tolerancia_planificacion": request.POST.get('tolerancia_planificacion'),
                "observaciones_gineco_obstetrico": request.POST.get('observaciones_gineco_obstetrico'),
            },
            "Antecedentes Hospitalizaciones": {
                "antecedente_hospitalizacion": request.POST.get('antecedente_hospitalizacion'),
                "causa_hospitalizacion": request.POST.get('causa_hospitalizacion'),
                "fecha_inicio_hospitalizacion": request.POST.get('fecha_inicio_hospitalizacion'),
                "duracion_hospitalizacion": request.POST.get('duracion_hospitalizacion'),
                "observaciones_hospitalizacion": request.POST.get('observaciones_hospitalizacion'),
            },
            "Antecedentes Inmunizaciones": {
                "antecedente_inmunizacion": request.POST.get('antecedente_inmunizacion'),
                "vacuna_inmunizacion": request.POST.get('vacuna_inmunizacion'),
                "numero_dosis_inmunizacion": request.POST.get('numero_dosis_inmunizacion'),
                "fecha_ultima_dosis_inmunizacion": request.POST.get('fecha_ultima_dosis_inmunizacion'),
                "observaciones_inmunizacion": request.POST.get('observaciones_inmunizacion'),
            },
            "Antecedentes Transfusionales": {
                "antecedente_transfusional": request.POST.get('antecedente_transfusional'),
                "motivo_transfusion": request.POST.get('motivo_transfusion'),
                "numero_dosis_transfusion": request.POST.get('numero_dosis_transfusion'),
                "fecha_ultima_dosis_transfusion": request.POST.get('fecha_ultima_dosis_transfusion'),
                "observaciones_transfusion": request.POST.get('observaciones_transfusion'),
            },
            "Antecedentes Familiares": {
                "antecedente_familiar": request.POST.get('antecedente_familiar'),
                "tipo_antecedente_familiar": request.POST.get('tipo_antecedente_familiar'),
                "parentesco_antecedente_familiar": request.POST.get('parentesco_antecedente_familiar'),
                "observaciones_antecedente_familiar": request.POST.get('observaciones_antecedente_familiar'),
            },
        }

        # Obtener la visita y el examen correspondiente
        visita_examen_id = request.POST.get('visita_examen')  # Asegúrate de pasar el ID de la visita en el formulario
        paciente_id = request.POST.get('paciente_id') 
        paciente = get_object_or_404(DatosDemograficos, id=paciente_id)
        documento_paciente = paciente.numero_documento
        
        # Obtener o crear el VisitaExamen correspondiente
        visita_examen, created = VisitaExamen.objects.get_or_create(
            id=visita_examen_id
        )
        
        # Crear o actualizar el registro de ResultadoExamen
        resultado_examen, created = ResultadoExamen.objects.get_or_create(
            visita_examen=visita_examen,
            paciente=paciente,
            defaults={'resultado': datos_formulario_antecedentes}
        )

        if not created:
            resultado_examen.resultado = datos_formulario_antecedentes
            resultado_examen.save()

        return redirect(reverse('detalle_paciente', args=[int(documento_paciente)]))
          
@login_required
def descargar_examen(request, visita_examen_id):
    visita_examen = VisitaExamen.objects.get(id=visita_examen_id)
    resultado_examen = ResultadoExamen.objects.filter(visita_examen=visita_examen).first()

    # Crear un buffer para el PDF
    buffer = BytesIO()

    # Crear el PDF
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, f"Examen: {visita_examen.examen.nombre}")
    p.drawString(100, 730, f"Fecha: {visita_examen.visita.fecha}")
    p.drawString(100, 710, f"Resultado: {resultado_examen.resultado}")
    p.showPage()
    p.save()

    # Obtener el valor del buffer y devolverlo como respuesta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="examen_{visita_examen.id}.pdf"'
    return response    