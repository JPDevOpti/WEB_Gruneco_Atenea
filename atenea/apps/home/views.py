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
from .models import DatosDemograficos, Proyecto, Examen, Visita, VisitaExamen,TipoVisita
from .forms import  ProyectoForm,RegistroDemograficoForm,AnamnesisForm
import json
from reportlab.pdfgen import canvas
from io import BytesIO
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
#from weasyprint import HTML
from .models import VisitaExamen

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

def perfil(request):
    context = {'segment': 'perfil'}
    html_template = loader.get_template('home/profile.html')
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
        form = RegistroDemograficoForm(request.POST, instance=paciente)  # Cargar los datos del paciente
        if form.is_valid():
            form.save()  # Guardar los cambios
            pacientes = DatosDemograficos.objects.all()
            messages.success(request, 'Datos demográficos editados exitosamente.')
    
            return render(request, 'home/tables.html', {'pacientes': pacientes})
    
        else:
            messages.error(request, f'❌ Error en el formulario. Verifica los campos. {str(form.errors)}')
            return render(request, 'sleepexams/editPacientForm.html', {'form': form})
            # Para depuración en la consola
        
  # Redirigir a una página de detalle del paciente
    if request.method == 'GET':
        form = RegistroDemograficoForm(instance=paciente)  # Cargar el formulario con los datos del paciente
        return render(request, 'sleepexams/editPacientForm.html', {'form': form})

@login_required
def detalle_paciente(request, paciente_id):
    proyectos = Proyecto.objects.all()
    paciente = get_object_or_404(DatosDemograficos, id=paciente_id)
    # Obtener los proyectos en los que el paciente ya está asignado
    proyectos_asociados = paciente.proyectos.all()
    # Obtener proyectos disponibles para asignación (excluye los que ya tiene)
    proyectos_disponibles = Proyecto.objects.exclude(id__in=proyectos_asociados.values_list('id', flat=True))
    
    # Obtener las visitas asociadas al paciente
    visitas_paciente = Visita.objects.filter(paciente=paciente)
    

    if request.method == "POST":
        proyecto_id = request.POST.get("proyecto_id")
        pacientes_ids = request.POST.get("paciente_id")  # Lista de IDs seleccionados

        proyecto = Proyecto.objects.get(id=proyecto_id)
        proyecto.pacientes.add(pacientes_ids)  # Asigna los pacientes al proyecto
        proyecto.save()
        
    return render(request, 'sleepexams/pacient.html', {'paciente': paciente,'proyectos':proyectos,'proyectos_asociados': proyectos_asociados,
        'proyectos_disponibles': proyectos_disponibles,'visitas_paciente': visitas_paciente,})

#proyectos
@login_required
def proyectos(request):
    proyectos = Proyecto.objects.all()
    examenes = Examen.objects.all()
    visitas = TipoVisita.objects.all()
    
    # Crear un diccionario para almacenar las visitas y exámenes por proyecto
    proyecto_data = {}
    for proyecto in proyectos:
        visitas_proyecto = visitas.filter(proyecto=proyecto)
        visitas_info = []
        for visita in visitas_proyecto:
            # Asegurar que los datos sean una lista de diccionarios
            examenes_data = visita.examenes if isinstance(visita.examenes, list) else json.loads(visita.examenes)

            # Extraer solo los IDs de los exámenes y convertirlos a enteros
            examenes_ids = [int(examen["id"]) for examen in examenes_data]
            
            # Buscar los nombres de los exámenes en la base de datos
            examenes_nombres = Examen.objects.filter(id__in=examenes_ids).values_list('nombre', flat=True)

            visitas_info.append({
                'id':visita.id,
                'nombre': visita.nombre,
                'observaciones': visita.observaciones,
                'examenes': examenes_nombres
            })
        proyecto_data[proyecto.id] = visitas_info
    
    context = {
        'proyectos': proyectos,
        'examenes': examenes,
        'visitas': visitas,
        'proyecto_data': proyecto_data
    }
    
    if request.method == 'POST':
        proyecto_form = ProyectoForm(request.POST)
        if proyecto_form.is_valid():
            proyecto_form.save()
            messages.success(request, 'Proyecto creado correctamente.')
            
        return redirect('proyectos')
    
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
    visitas = TipoVisita.objects.all()
    
    # Crear un diccionario para almacenar las visitas y exámenes por proyecto
    proyecto_data = {}
    for proyecto in proyectos:
        visitas_proyecto = visitas.filter(proyecto=proyecto)
        visitas_info = []
        for visita in visitas_proyecto:
            # Asegurar que los datos sean una lista de diccionarios
            examenes_data = visita.examenes if isinstance(visita.examenes, list) else json.loads(visita.examenes)

            # Extraer solo los IDs de los exámenes y convertirlos a enteros
            examenes_ids = [int(examen["id"]) for examen in examenes_data]
            
            # Buscar los nombres de los exámenes en la base de datos
            examenes_nombres = Examen.objects.filter(id__in=examenes_ids).values_list('nombre', flat=True)
            visitas_info.append({
                'id':visita.id,
                'nombre': visita.nombre,
                'observaciones': visita.observaciones,
                'examenes': examenes_nombres,
            })
        proyecto_data[proyecto.id] = visitas_info
    
    context = {
        'proyectos': proyectos,
        'examenes': examenes,
        'visitas': visitas,
        'proyecto_data': proyecto_data
    }
   
    if request.method == 'POST':
        proyecto_id = request.POST.get('proyecto_id')
        nombres = request.POST.getlist('nombre_visita[]')  # Varias visitas
        observaciones_list = request.POST.getlist('observaciones[]')
        
        # Recibir el JSON desde el formulario y decodificarlo
        examenes_json = request.POST.get('examenes_json', '[]')
        examenes_lista = json.loads(examenes_json)  # Convertir a lista de diccionarios

        for i in range(len(nombres)):  # Crear una visita por cada nombre recibido
            TipoVisita.objects.create(
                proyecto_id=proyecto_id,
                nombre=nombres[i],
                observaciones=observaciones_list[i],
                examenes=examenes_lista  # Guardar la lista completa de exámenes como JSON
            )

        return redirect('proyectos')

    return render(request, 'home/proyectos.html',context)

@login_required
def eliminar_visita(request, id):
    # Obtener la visita o devolver un error 404 si no existe
    visita = get_object_or_404(TipoVisita, id=id)

    if request.method == "POST":
        
        # Luego, eliminar la visita
        visita.delete()

        # Mensaje de confirmación
        messages.success(request, "La visita ha sido eliminada correctamente.")

        return redirect('proyectos')  # Redirigir a la lista de proyectos o donde corresponda

    return redirect('proyectos')

from django.shortcuts import render, get_object_or_404, redirect
from .models import DatosDemograficos, Proyecto, TipoVisita, Visita

def crear_visita(request, paciente_id):
    paciente = get_object_or_404(DatosDemograficos, id=paciente_id)
    proyectos_asociados = paciente.proyectos.all()

    # Obtener los proyectos en los que el paciente ya está asignado
    proyectos_disponibles = Proyecto.objects.exclude(id__in=proyectos_asociados.values_list('id', flat=True))
    
    # Obtener los tipos de visita disponibles para estos proyectos
    tipo_visitas = TipoVisita.objects.filter(proyecto__in=proyectos_asociados)
    
    if request.method == "POST":
        proyecto_id = request.POST.get("proyecto_id")
        tipo_visita_id = request.POST.get("tipo_visita")
        fecha = request.POST.get("fecha")
        evaluador = request.POST.get("evaluador")
        nombre = request.POST.get("nombre")
        
        # Capturar datos del acompañante
        acompanante_nombre = request.POST.get("acompanante_nombre")
        acompanante_relacion = request.POST.get("acompanante_relacion")
        acompanante_correo = request.POST.get("acompanante_correo")
        acompanante_telefono = request.POST.get("acompanante_telefono")
        
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        tipo_visita = get_object_or_404(TipoVisita, id=tipo_visita_id)

        # Crear la visita y asignarla al paciente
        nueva_visita = Visita.objects.create(
            paciente=paciente,
            nombre=nombre,
            Tipo_visita=tipo_visita,
            fecha=fecha,
            evaluador=evaluador,
            acompanante_nombre=acompanante_nombre,
            acompanante_relacion=acompanante_relacion,
            acompanante_correo=acompanante_correo,
            acompanante_telefono=acompanante_telefono
        )
        
        # Procesar los exámenes seleccionados
        examenes_seleccionados = request.POST.get('examenes_seleccionados')
        if examenes_seleccionados:
            try:
                lista_ids_examenes = json.loads(examenes_seleccionados)
                print(f"Exámenes seleccionados para la visita {nueva_visita.id}: {lista_ids_examenes}")
                
                # Crear un registro VisitaExamen para cada examen seleccionado
                for examen_id in lista_ids_examenes:
                    examen = Examen.objects.get(id=examen_id)
                    VisitaExamen.objects.create(
                        visita=nueva_visita,
                        examen=examen,
                        # El campo resultado quedará como NULL
                        # Los resultados se agregarán en otra función
                    )
                
                # Mensaje de éxito
                messages.success(request, f"Visita creada con éxito con {len(lista_ids_examenes)} exámenes asociados.")
                
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON de exámenes: {examenes_seleccionados}")
                print(f"Error específico: {str(e)}")
                messages.error(request, "Error al procesar los exámenes seleccionados.")
            
            # Mensaje de éxito
            messages.success(request, f"Visita  creada con éxito con {len(lista_ids_examenes)} exámenes asociados.")
        
        return redirect('detalle_paciente', paciente_id=paciente.id)  # Redirige después de crear

    return render(request, 'sleepexams/pacient.html', {
        'paciente': paciente,
        'proyectos_asociados': proyectos_asociados,
        'proyectos_disponibles': proyectos_disponibles,
        'tipo_visitas': tipo_visitas
    })

def eliminar_v(request, visita_id):
    visita = get_object_or_404(Visita, id=visita_id)
    paciente_id = visita.paciente.id  # Para redirigir después de eliminar
    
    visita.delete()
    messages.success(request, "Visita eliminada correctamente.")
    
    return redirect('detalle_paciente', paciente_id=paciente_id)

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
@login_required
def realizar_examen(request, visita_id, examen_id, paciente_id):

    # Diccionario de plantillas según el examen
    exam_templates = {
        3: "sleepexams/General_ExamenFísico.html",
        4: "sleepexams/General_RevisiónSistemas.html",
        5: "sleepexams/General_Antecedentes.html",
        7: "sleepexams/General_Análisis.html",
        8: "sleepexams/General_Medicamentos.html",
        9: "sleepexams/General_ExamenNeurológico.html",
        10: "sleepexams/Sueno_anamnesis.html",
        11: "sleepexams/Sueño_Cuestionarios.html",
        12: "sleepexams/Sueño_ExamenFisico.html",
    }

    template = exam_templates.get(examen_id, "sleepexams/anamnesisTest.html")  

    return render(request, template, {'visita_examen': visita_id, 'paciente_id':paciente_id,'examen_id':examen_id})

@login_required
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
        documento_paciente = paciente.id
 

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

@login_required
def guardar_examen_fisico(request):
    if request.method == 'POST':

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
        documento_paciente = paciente.id
        
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

@login_required
def guardar_examen_antecedentes(request):
    if request.method == 'POST':
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
        visita_id = request.POST.get('visita_id')
        examen_id = request.POST.get('examen_id')
        # Obtener las instancias de Visita y Examen
        visita = get_object_or_404(Visita, id=visita_id)
        examen = get_object_or_404(Examen, id=examen_id)
        
        paciente_id = request.POST.get('paciente_id') 
        paciente = get_object_or_404(DatosDemograficos, id=paciente_id)
        documento_paciente = paciente.id
        
        # Obtener o crear el VisitaExamen con la relación correcta
        visita_examen, created = VisitaExamen.objects.get_or_create(
            visita=visita, examen=examen
        )

        # Si ya tiene un resultado, lo actualizamos
        if visita_examen.resultado:
            visita_examen.resultado.update(datos_formulario_antecedentes)
        else:
            visita_examen.resultado = datos_formulario_antecedentes

        # Guardar cambios
        visita_examen.save()

        return redirect(reverse('detalle_paciente', args=[int(documento_paciente)]))

@login_required
def guardar_examen_analisis(request):
     if request.method == "POST":

        # Estructura del análisis del examen
        datos_formulario_analisis = {
            "Analisis": {
                "analisis_historia": request.POST.get("analisis_historia", ""),
                "plan_tratamiento": request.POST.get("plan_tratamiento", ""),
                "Diagnosticos_CIE10": [],
                "Diagnosticos_DSMV": []
            }
        }

        # Obtener listas de diagnósticos CIE-10
        cie10_codigos = request.POST.getlist("cie10_codigo[]")
        cie10_diagnosticos = request.POST.getlist("cie10_diagnostico[]")
        cie10_estados = request.POST.getlist("cie10_estado[]")

        # Agregar diagnósticos CIE-10 a la estructura
        for i in range(len(cie10_codigos)):
            datos_formulario_analisis["Analisis"]["Diagnosticos_CIE10"].append({
                "codigo": cie10_codigos[i],
                "diagnostico": cie10_diagnosticos[i],
                "estado": cie10_estados[i] if i < len(cie10_estados) else None
            })

        # Obtener listas de diagnósticos DSM-V
        dsmv_codigos = request.POST.getlist("dsmv_codigo[]")
        dsmv_diagnosticos = request.POST.getlist("dsmv_diagnostico[]")
        dsmv_estados = request.POST.getlist("dsmv_estado[]")

        # Agregar diagnósticos DSM-V a la estructura
        for i in range(len(dsmv_codigos)):
            datos_formulario_analisis["Analisis"]["Diagnosticos_DSMV"].append({
                "codigo": dsmv_codigos[i],
                "diagnostico": dsmv_diagnosticos[i],
                "estado": dsmv_estados[i] if i < len(dsmv_estados) else None
            })

         # Obtener la visita y el examen correspondiente
        visita_id = request.POST.get('visita_id')
        examen_id = request.POST.get('examen_id')
        # Obtener las instancias de Visita y Examen
        visita = get_object_or_404(Visita, id=visita_id)
        examen = get_object_or_404(Examen, id=examen_id)
        
        paciente_id = request.POST.get('paciente_id') 
        paciente = get_object_or_404(DatosDemograficos, id=paciente_id)
        documento_paciente = paciente.id
        
        # Obtener o crear el VisitaExamen con la relación correcta
        visita_examen, created = VisitaExamen.objects.get_or_create(
            visita=visita, examen=examen
        )

        # Si ya tiene un resultado, lo actualizamos
        if visita_examen.resultado:
            visita_examen.resultado.update(datos_formulario_analisis)
        else:
            visita_examen.resultado = datos_formulario_analisis

        # Guardar cambios
        visita_examen.save()

        return redirect(reverse('detalle_paciente', args=[int(documento_paciente)]))

@login_required 
def guardar_examen_neurologico(request):
    if request.method == 'POST':
        # Obtener los datos del formulario para antecedentes
        datos_formulario_antecedentes = {
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
            }
        }

        # Obtener la visita y el examen correspondiente
        visita_examen_id = request.POST.get('visita_examen')  # Asegúrate de pasar el ID de la visita en el formulario
        paciente_id = request.POST.get('paciente_id') 
        paciente = get_object_or_404(DatosDemograficos, id=paciente_id)
        documento_paciente = paciente.id
        
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
def guardar_examen_medicamentos(request):
    if request.method == 'POST':
        print("aqui")
        # Obtener los datos del formulario para antecedentes epidemiológicos
        datos_formulario_medicamentos = {
        "Medicamentos": []
            }

        # Obtener las listas de medicamentos del formulario (coincidiendo con los nombres en el HTML)
        nombres_comerciales = request.POST.getlist('nombre_comercial[]')
        nombres_genericos = request.POST.getlist('nombre_generico[]')
        presentaciones = request.POST.getlist('presentacion[]')
        concentraciones = request.POST.getlist('concentracion[]')
        unidades = request.POST.getlist('unidad[]')
        vias_administracion = request.POST.getlist('via_administracion[]')
        cantidades = request.POST.getlist('cantidad[]')
        frecuencias = request.POST.getlist('frecuencia[]')
        fechas_inicio = request.POST.getlist('fecha_inicio[]')
        fechas_finalizacion = request.POST.getlist('fecha_finalizacion[]')
        indicaciones = request.POST.getlist('indicacion[]')

        # Iterar sobre las listas y construir la lista de medicamentos
        for i in range(len(nombres_comerciales)):
            datos_formulario_medicamentos["Medicamentos"].append({
                "nombre_comercial": nombres_comerciales[i],
                "nombre_generico": nombres_genericos[i],
                "presentacion": presentaciones[i],
                "concentracion": concentraciones[i],
                "unidad": unidades[i],
                "via_administracion": vias_administracion[i],
                "cantidad": cantidades[i],
                "frecuencia": frecuencias[i],
                "fecha_inicio": fechas_inicio[i],
                "fecha_finalizacion": fechas_finalizacion[i],
                "indicacion": indicaciones[i]
            })

         # Obtener la visita y el examen correspondiente
        visita_id = request.POST.get('visita_id')
        examen_id = request.POST.get('examen_id')
        # Obtener las instancias de Visita y Examen
        visita = get_object_or_404(Visita, id=visita_id)
        examen = get_object_or_404(Examen, id=examen_id)
        
        paciente_id = request.POST.get('paciente_id') 
        paciente = get_object_or_404(DatosDemograficos, id=paciente_id)
        documento_paciente = paciente.id
        
        # Obtener o crear el VisitaExamen con la relación correcta
        visita_examen, created = VisitaExamen.objects.get_or_create(
            visita=visita, examen=examen
        )

        # Si ya tiene un resultado, lo actualizamos
        if visita_examen.resultado:
            visita_examen.resultado.update(datos_formulario_medicamentos)
        else:
            visita_examen.resultado = datos_formulario_medicamentos

        # Guardar cambios
        visita_examen.save()

        return redirect(reverse('detalle_paciente', args=[int(documento_paciente)]))

@login_required
def guardar_examen_anamnesis(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        datos_formulario_anamnesis = {
            "Motivo de consulta": request.POST.get('motivo_consulta'),
            "Enfermedad actual": request.POST.get('enfermedad_actual'),
            "Quejas de sueño": [],
            "Horario de sueño": {
                "rutina_dormir": request.POST.get('rutina_dormir'),
                "describa_rutina": request.POST.get('describa_rutina'),
                "jornada_laboral": request.POST.getlist('jornada_laboral[]'),
                "hora_acostarse_laboral": request.POST.get('hora_acostarse_laboral'),
                "tiempo_dormirse_laboral": request.POST.get('tiempo_dormirse_laboral'),
                "hora_intencion_dormir_laboral": request.POST.get('hora_intencion_dormir_laboral'),
                "hora_despertar_laboral": request.POST.get('hora_despertar_laboral'),
                "tiempo_salir_cama_laboral": request.POST.get('tiempo_salir_cama_laboral'),
                "sueno_reparador_laboral": request.POST.get('sueno_reparador_laboral'),
                "companero_cama_laboral": request.POST.get('companero_cama_laboral'),
                "despertador_laboral": request.POST.get('despertador_laboral'),
                "jornada_fds": request.POST.getlist('jornada_fds[]'),
                "hora_acostarse_fds": request.POST.get('hora_acostarse_fds'),
                "tiempo_dormirse_fds": request.POST.get('tiempo_dormirse_fds'),
                "hora_intencion_dormir_fds": request.POST.get('hora_intencion_dormir_fds'),
                "hora_despertar_fds": request.POST.get('hora_despertar_fds'),
                "tiempo_salir_cama_fds": request.POST.get('tiempo_salir_cama_fds'),
                "sueno_reparador_fds": request.POST.get('sueno_reparador_fds'),
                "companero_cama_fds": request.POST.get('companero_cama_fds'),
                "despertador_fds": request.POST.get('despertador_fds'),
                "hora_acostarse_vacaciones": request.POST.get('hora_acostarse_vacaciones'),
                "tiempo_dormirse_vacaciones": request.POST.get('tiempo_dormirse_vacaciones'),
                "hora_intencion_dormir_vacaciones": request.POST.get('hora_intencion_dormir_vacaciones'),
                "hora_despertar_vacaciones": request.POST.get('hora_despertar_vacaciones'),
                "tiempo_salir_cama_vacaciones": request.POST.get('tiempo_salir_cama_vacaciones'),
                "sueno_reparador_vacaciones": request.POST.get('sueno_reparador_vacaciones'),
                "companero_cama_vacaciones": request.POST.get('companero_cama_vacaciones'),
                "despertador_vacaciones": request.POST.get('despertador_vacaciones'),
            },
            "higiene del sueno":{ 
           
            "Siestas": {
                "realiza_siestas": request.POST.get('realiza_siestas'),
                "numero_siestas": request.POST.get('numero_siestas'),
                "duracion_siestas": request.POST.get('duracion_siestas'),
                "siesta_frecuencia": request.POST.get('siesta_frecuencia'),
                "momento_dia": request.POST.getlist('momento_dia[]'),  # Lista de momentos del día
                "siesta_reparadora": request.POST.get('siesta_reparadora'),
                "periodo_siestas": request.POST.get('periodo_siestas'),
            },
            "Lugar_donde_duerme": {
                "iluminacion": request.POST.getlist('iluminacion[]'),  # Lista de condiciones de iluminación
                "comodidad": request.POST.getlist('comodidad[]'),  # Lista de comodidad del espacio
                "ruido": request.POST.getlist('ruido[]'),  # Lista de condiciones de ruido
            },
            "Consumo_comidas_bebidas": {
                "consume": request.POST.get('consume'),
                "sustancias": [],  # Lista de sustancias dinámicas
            },
            "Medicamentos": {
                "consume_medicamento": request.POST.get('consume_medicamento'),
                "medicamentos": [],  # Lista de medicamentos dinámicos
            },
            "Uso_pantallas": {
                "usa_pantallas": request.POST.get('usa_pantallas'),
                "pantallas": [],  # Lista de pantallas dinámicas
            },
            "Actividades_en_cama": {
                "cama_actividades": request.POST.get('cama_actividades'),
                "actividades": [],  # Lista de actividades dinámicas
            },
            "Actividad_fisica": {
                "actividad_fisica": request.POST.get('actividad_fisica'),
                "actividades_fisicas": [],  # Lista de actividades físicas dinámicas
            },
            },
            "síntoma diferente asociado al sueño":{
                 "sintomas": {
                "sintomas_sueno": request.POST.get('sintomas_sueno'),
                "sueno": [],  # Lista de actividades dinámicas
            },
            "síntoma durante el funcionamiento diurno": {
                "actividad_diurno": request.POST.get('sintomas_diurnos'),
                "actividades_funcionamiento_diurno": [],  # Lista de actividades físicas dinámicas
            },
            }
        }

         # Obtener las quejas de sueño dinámicas
        quejas = request.POST.getlist('tipo_queja[]')  # Lista de quejas seleccionadas
        for i in range(len(quejas)):  # Usar el índice para recuperar los campos dinámicos
            datos_queja = {
                "tipo_queja": quejas[i],
                "inicio": request.POST.get(f'inicio_{i}'),
                "evolucion": request.POST.get(f'evolucion_{i}'),
                "frecuencia_semana": request.POST.get(f'frecuencia_{i}'),
                "gravedad": request.POST.get(f'gravedad_{i}'),
            }
            datos_formulario_anamnesis["Quejas de sueño"].append(datos_queja)
            
        # Obtener las sustancias dinámicas
        # Obtener las sustancias dinámicas
        i = 0
        while True:
            tipo_sustancia = request.POST.get(f'tipo_sustancia_{i}')
            if not tipo_sustancia:  # Si no hay más sustancias, salir del bucle
                break

            datos_sustancia = {
                "tipo_sustancia": tipo_sustancia,
                "cantidad_sustancia": request.POST.get(f'cantidad_sustancia_{i}'),
                "frecuencia_sustancia": request.POST.get(f'frecuencia_sustancia_{i}'),
                "tiempo_sustancia": request.POST.get(f'tiempo_sustancia_{i}'),
                "observaciones_sustancia": request.POST.get(f'observaciones_sustancia_{i}'),
            }
            datos_formulario_anamnesis["higiene del sueno"]["Consumo_comidas_bebidas"]["sustancias"].append(datos_sustancia)
            i += 1
            
        # Obtener los medicamentos dinámicos
        medicamentos = request.POST.getlist('nombre_medicamento[]')  # Lista de medicamentos seleccionados
        datos_medicamentos = []  # Lista para almacenar la información de cada medicamento

        for i in range(len(medicamentos)):
            datos_medicamento = {
                "nombre_medicamento": medicamentos[i],
                "dosis_medicamento": request.POST.getlist('dosis_medicamento[]')[i],
                "observaciones_medicamento": request.POST.getlist('observaciones_medicamento[]')[i],
                "presentacion": request.POST.getlist('presentacion[]')[i],
                "veces_dia": request.POST.getlist('veces_dia[]')[i],
                "frecuencia_medicamentos": request.POST.getlist('frecuencia_medicamentos[]')[i],
                "tiempo": request.POST.getlist('tiempo_antes_dormir[]')[i],
            }
            datos_formulario_anamnesis["higiene del sueno"]["Medicamentos"]["medicamentos"].append(datos_medicamento)
    
        # Obtener las pantallas dinámicas
        # Obtener las pantallas dinámicas
        pantallas = request.POST.getlist('tipo_pantalla[]')
        frecuencias = request.POST.getlist('pantalla_frecuencia[]')
        tiempos_antes_dormir = request.POST.getlist('pantalla_tiempo_dormir[]')


        for i in range(len(pantallas)):
            datos_pantalla = {
                "tipo_pantalla": pantallas[i],
                "frecuencia_pantalla": frecuencias[i],
                "tiempo_antes_dormir": tiempos_antes_dormir[i],
            }
            datos_formulario_anamnesis["higiene del sueno"]["Uso_pantallas"]["pantallas"].append(datos_pantalla)
        # Obtener las actividades en la cama dinámicas
        
        
        tipo_actividad = request.POST.getlist('tipo_actividad[]')  # Lista con actividades seleccionadas
        frecuencia_actividad = request.POST.getlist('frecuencia_actividad[]')  # Lista de frecuencias
        observaciones = request.POST.getlist('observaciones_actividades[]')  # Lista de observaciones
        
        for i, actividad in enumerate(tipo_actividad):
            datos_actividad = {
                "tipo_actividad": tipo_actividad[i],
                "frecuencia_actividad_otro_text": frecuencia_actividad[i],
                "observaciones_actividad": observaciones[i],
            }
            datos_formulario_anamnesis["higiene del sueno"]["Actividades_en_cama"]["actividades"].append(datos_actividad)

        # Obtener las actividades físicas dinámicas
        actividades_fisicas = request.POST.getlist('tipo_actividad_fisica[]') 
        tipo_actividad_otro_texto = request.POST.getlist('tipo_actividad_otro_texto[]')  # Lista con actividades seleccionadas
        intensidad_fisica = request.POST.getlist('intensidad_fisica[]')  # Lista de frecuencias
        frecuencia_fisica = request.POST.getlist('frecuencia_fisica[]')
        observaciones_actividad_fisica = request.POST.getlist('observaciones_actividad_fisica[]')
        
        # Lista de actividades físicas seleccionadas
        for i, actividad_fisica in enumerate(actividades_fisicas):
            datos_actividad_fisica = {
                "actividades_fisicas": actividades_fisicas[i],
                "tipo_actividad_otro_texto": tipo_actividad_otro_texto[i],
                "intensidad_fisica": intensidad_fisica[i],
                "frecuencia_fisica": frecuencia_fisica[i],
                "observaciones_actividad_fisica": observaciones_actividad_fisica[i],
            }
            datos_formulario_anamnesis["higiene del sueno"]["Actividad_fisica"]["actividades_fisicas"].append(datos_actividad_fisica)


        ##################################################################################################3
        # Obtener Síntoma diferente asociado al sueño
        tipo_sintoma = request.POST.getlist('tipo_sintoma[]') 
        cuando_inicio = request.POST.getlist('cuando_inicio[]')  # Lista con actividades seleccionadas
        evolucion = request.POST.getlist('evolucion[]')  # Lista de frecuencias
        frecuencia = request.POST.getlist('frecuencia[]')
        gravedad = request.POST.getlist('gravedad[]')
        observaciones_sintoma = request.POST.getlist('observaciones_sintoma[]')
        
          # Lista de actividades físicas seleccionadas
        for i, actividad_fisica in enumerate(tipo_sintoma):
            datos_sintoma_sueno = {
                "tipo_sintoma": tipo_sintoma[i],
                "cuando_inicio": cuando_inicio[i],
                "evolucion": evolucion[i],
                "frecuencia": frecuencia[i],
                "gravedad": gravedad[i],
                "observaciones_sintoma": observaciones_sintoma[i],
            }
            datos_formulario_anamnesis["síntoma diferente asociado al sueño"]["sintomas"]["sueno"].append(datos_sintoma_sueno)


        # Obtener Síntoma diferente asociado al sueño
        tipo_sintoma_diurno = request.POST.getlist('tipo_sintoma_diurno[]') 
        cuando_inicio_diurno = request.POST.getlist('cuando_inicio_diurno[]')  # Lista con actividades seleccionadas
        evolucion_diurno = request.POST.getlist('evolucion_diurno[]')  # Lista de frecuencias
        frecuencia_diurno = request.POST.getlist('frecuencia_diurno[]')
        gravedad_diurno = request.POST.getlist('gravedad_diurno[]')
        observaciones_sintoma_diurno = request.POST.getlist('observaciones_sintoma_diurno[]')
        
          # Lista de actividades físicas seleccionadas
        for i, actividad_fisica in enumerate(tipo_sintoma_diurno):
            datos_sintoma_diurno = {
                "tipo_sintoma_diurno": tipo_sintoma_diurno[i],
                "cuando_inicio_diurno": cuando_inicio_diurno[i],
                "evolucion_diurno": evolucion_diurno[i],
                "frecuencia_diurno": frecuencia_diurno[i],
                "gravedad_diurno": gravedad_diurno[i],
                "observaciones_sintoma_diurno": observaciones_sintoma_diurno[i],
            }
            datos_formulario_anamnesis["síntoma diferente asociado al sueño"]["síntoma durante el funcionamiento diurno"]["actividades_funcionamiento_diurno"].append(datos_sintoma_diurno)

        # Aquí puedes guardar los datos en la base de datos o procesarlos como necesites
        print(datos_formulario_anamnesis)  # Solo para verificar los datos en la consola

        # Obtener la visita y el examen correspondiente
        visita_id = request.POST.get('visita_id')
        examen_id = request.POST.get('examen_id')
        # Obtener las instancias de Visita y Examen
        visita = get_object_or_404(Visita, id=visita_id)
        examen = get_object_or_404(Examen, id=examen_id)
        
        paciente_id = request.POST.get('paciente_id') 
        paciente = get_object_or_404(DatosDemograficos, id=paciente_id)
        documento_paciente = paciente.id
        
        # Obtener o crear el VisitaExamen con la relación correcta
        visita_examen, created = VisitaExamen.objects.get_or_create(
            visita=visita, examen=examen
        )

        # Si ya tiene un resultado, lo actualizamos
        if visita_examen.resultado:
            visita_examen.resultado.update(datos_formulario_anamnesis)
        else:
            visita_examen.resultado = datos_formulario_anamnesis

        # Guardar cambios
        visita_examen.save()

        return redirect(reverse('detalle_paciente', args=[int(documento_paciente)]))

@login_required 
def guardar_examen_sueno_fisico(request):
    if request.method == 'POST':
        # Obtener los datos del formulario para antecedentes
        datos_formulario_sueno_fisico = {
            "Peso (Kg)": request.POST.get("peso"),
            "Talla (cm)": request.POST.get("talla"),
            "Índice de Masa Corporal (IMC)": request.POST.get("imc"),
            "Rango IMC": request.POST.get("rango_imc"),
            "Circunferencia de cuello": request.POST.get("circunferencia_cuello"),
            "Perímetro abdominal": request.POST.get("perimetro_abdominal"),
            "Simetría de las narinas": request.POST.get("simetria_narinas"),
            "Tipo de narina": request.POST.get("tipo_narina"),
            "Presencia de desviación de septo": request.POST.get("desviacion_septo"),
            "Hipertrofia de cornetes nasales": request.POST.get("hipertrofia_cornetes"),
            "Grado": request.POST.get("grado"),
            "Hipertrofi de úvula": request.POST.get("hipertrofia_uvula"),
            "Biotipo": request.POST.get("biotipo"),
            "Clasificación de Mallampati": request.POST.get("mallampati"),
            "Hipertrofía de amigdalas (Escala de Friedman)": request.POST.get("amigdalas"),
            "Tipo de mordida": request.POST.get("tipo_mordida"),
            "Alteración cráneo o cara": request.POST.get("alteracion_craneo"),
            }
            
        

         # Aquí puedes guardar los datos en la base de datos o procesarlos como necesites
        print(datos_formulario_sueno_fisico)  # Solo para verificar los datos en la consola

        # Obtener la visita y el examen correspondiente
        visita_id = request.POST.get('visita_id')
        examen_id = request.POST.get('examen_id')
        # Obtener las instancias de Visita y Examen
        visita = get_object_or_404(Visita, id=visita_id)
        examen = get_object_or_404(Examen, id=examen_id)
        
        paciente_id = request.POST.get('paciente_id') 
        paciente = get_object_or_404(DatosDemograficos, id=paciente_id)
        documento_paciente = paciente.id
        
        # Obtener o crear el VisitaExamen con la relación correcta
        visita_examen, created = VisitaExamen.objects.get_or_create(
            visita=visita, examen=examen
        )

        # Si ya tiene un resultado, lo actualizamos
        if visita_examen.resultado:
            visita_examen.resultado.update(datos_formulario_sueno_fisico)
        else:
            visita_examen.resultado = datos_formulario_sueno_fisico

        # Guardar cambios
        visita_examen.save()

        return redirect(reverse('detalle_paciente', args=[int(documento_paciente)]))


@login_required
def guardar_examen_Sueño_Cuestionarios(request):
    if request.method == 'POST':
        # Obtener los datos del formulario para antecedentes
        datos_formulario_Cuestionarios = {
            "Pittsburgh": {
                "Hora de acostarse durante el ultimo mes": request.POST.get('hora_acostarse'),
                "Latencia de inicio de sueño (minutos)": request.POST.get('latencia_sueno'),
                "Hora de levantarse durante el ultimo mes": request.POST.get('hora_levantarse'),
                "Cuantas horas duerme verdaderamente cada noche durante el ultimo mes": request.POST.get('horas_dormidas'),
                "No poder conciliar el sueño": request.POST.get('conciliar_sueno'),
                "Despertarse durante la noche o de madrugada": request.POST.get('despertarse_sueno'),
                "Tener que levantarse para ir al servicio": request.POST.get('levantarse_servicio_sueno'),
                "No poder respirar bien": request.POST.get('respirar'),
                "Toser o roncar ruidosamente": request.POST.get('toser_roncar_sueno'),
                "Sentir frio": request.POST.get('Sentir_frio_sueno'),
                "Sentir demasiado calor": request.POST.get('calor_sueno'),
                "Tener pesadillas o malos sueños" : request.POST.get('pesadillas_sueno'),
                "Sufrir dolores": request.POST.get('dolores_sueno'),
                
                # Nuevos campos agregados
                "otras_razones": request.POST.get('otras'),
                "otras_sueno": request.POST.get('otras_sueno'),
                "Durante el ultimo mes ¿Como valoraria en conjunto su calidad de sueño?": request.POST.get('calidad_sueno'),
                "Durante el ultimo mes ¿Cuantas veces habra tomado medicinas (por su cuenta o recetadas por medico) para dormir?": request.POST.get('medicinas_sueno'),
                "Durante el ultimo mes ¿Cuantas veces ha sentido somnolencia mientras conducia, comia, o desarrollaba alguna otra actividad?": request.POST.get('somnolencia_sueno'),
                "Durante el ultimo mes ¿ha representado mucho problema el tener animos para realizar alguna de las actividades detalladas en la pregunta anterior?": request.POST.get('problemas_animos_sueno'),
                "Duerme solo o acompañado": request.POST.get('duerme_acompanado'),
                
                # Campos mostrados solo si duerme acompañado
                "Ronquidos ruidosos": request.POST.get('ronquidos_ruidosos'),
                "Grandes pausas entre respiraciones mientras duerme": request.POST.get('pausas_respiracion'),
                "Sacudidas o espasmos de piernas mientras duerme": request.POST.get('sacudidas_piernas'),
                "Episodios de desorientación o confusión mientras duerme": request.POST.get('desorientacion_confusion'),
                "Otros inconvenientes mientras duerme (describir)": request.POST.get('otros_inconvenientes'),
                "descripcion_inconvenientes": request.POST.get('descripcion_inconvenientes'),
            },
            "Epworth": {
                "Con que frecuencia se queda dormido?": {
                "Sentado y leyendo": request.POST.get('epworth_leyendo'),
                "Viendo la TV": request.POST.get('epworth_tv'),
                "Sentado, inactivo en un espectáculo (teatro)": request.POST.get('epworth_teatro'),
                "En coche, como piloto de un viaje de una hora": request.POST.get('epworth_piloto'),
                "Tumbado a media tarde": request.POST.get('epworth_tumbado'),
                "Sentado y charlando con alguien": request.POST.get('epworth_charlando'),
                "Sentado después de comer sin ingerir alcohol": request.POST.get('epworth_comida'),
                "En su coche, cuando se para debido al tráfico": request.POST.get('epworth_trafico'),
                }
                },
            "Stop_Bang" : {
                    "Ronca fuerte": request.POST.get('ronca_fuerte', 'No'),
                    "Se siente cansado con frecuencia": request.POST.get('cansado_frecuencia', 'No'),
                    "Lo observaron dejar de respirar o ahogarse mientras dormía": request.POST.get('deja_respirar', 'No'),
                    "Tiene o está recibiendo tratamiento para la presión arterial": request.POST.get('presion_arterial', 'No'),
                    "Presenta un índice de masa corporal de más de 35kg/m²": request.POST.get('imc_alto', 'No'),
                    "Tiene más de 50 años": request.POST.get('mayor_50', 'No'),
                    "El tamaño de su cuello es grande": request.POST.get('cuello_grande', 'No'),
                    "Masculino": request.POST.get('masculino', 'No'),
                },
            "MEQ" :{
                "Hora a la que se levantaría si fuera libre de planificar el día": request.POST.get('hora_levantarse_meq'),
                "Hora a la que se acostaría": request.POST.get('hora_acostarse_meq'),
                "Necesidad del despertador para levantarse": request.POST.get('uso_despertador_meq'),
                "Facilidad para levantarse por la mañana": request.POST.get('facilidad_levantarse_meq'),
                "Nivel de alerta en la primera media hora tras levantarse": request.POST.get('alerta_manana_meq'),
                "Apetito en la primera media hora tras levantarse": request.POST.get('apetito_manana_meq'),
                "Sensación de descanso en la primera media hora tras levantarse": request.POST.get('descanso_manana_meq'),
                "Hora a la que se acostaría en un día sin compromisos": request.POST.get('hora_acostarse_libre_meq'),
                "Estado físico al realizar ejercicio por la mañana": request.POST.get('ejercicio_fisico_meq'),
                "Hora aproximada de la noche en que se siente cansado": request.POST.get('hora_cansancio_noche_meq'),
                "Horario ideal para una prueba mentalmente agotadora": request.POST.get('horario_prueba_mental_meq'),
                
                "Si te acostaras a las 11 PM, ¿qué nivel de cansancio notarías?": request.POST.get('nivel_cansancia_11'),
                "por algún motivo te has acostado varias horas más tarde..¿Cuando crees que te despertarías? ": request.POST.get('hora_despertarse_si_tarde'),
                
                "Guardia nocturna, ¿qué preferirías? ": request.POST.get("guardia_nocturna"),
                "Tienes que hacer dos horas de trabajo físico pesado.  ¿qué horario escogerías?": request.POST.get("horario_trabajo_fisico"),
                "Has decidido hacer ejercicio físico intenso nocturno. ¿Cómo crees que te sentaría?": request.POST.get("ejercicio_nocturno"),
                "horario trabajo, ¿Qué CINCO HORAS CONSECUTIVAS seleccionarías? ¿Empezando en qué hora?": request.POST.get("horario_trabajo"),
                "¿A qué hora del día crees que alcanzas tu máximo bienestar?": request.POST.get("maximo_bienestar"),
                "Se habla de personas de tipo matutino y vespertino. ¿Cuál de estos tipos te consideras ser?": request.POST.get("tipo_persona"),
                "puntuacion": request.POST.get("puntuacion"),
            },
            "Berlín": {
                "¿Su peso ha cambiado en los últimos 5 años?": request.POST.get("peso_cambio"),
                "¿Usted ronca?": request.POST.get("ronca"),
                "Si usted ronca, ¿Su ronquido es?": request.POST.get("tipo_ronquido"),
                "¿Con qué frecuencia ronca?": request.POST.get("frecuencia_ronquidos"),
                "¿Alguna vez su ronquido ha molestado a otras personas?": request.POST.get("ronquido_molesto"),
                "¿Ha notado alguien que usted deja de respirar cuando duerme?": request.POST.get("apnea_observada"),
                "¿Se siente cansado o fatigado al levantarse por la mañana?": request.POST.get("fatiga_matutina"),
                "fatiga_dia": request.POST.get("fatiga_dia"),
                "¿Alguna vez se ha sentido somnoliento o se ha quedado dormido mientras va de pasajero en un carro o maneja un vehículo?": request.POST.get("somnolencia_conducir"),
                "¿Usted tiene la presión alta?": request.POST.get("presion_alta"),
            },
            "Atenas":{
                "Inducción del dormir (tiempo que le toma quedarse dormido una vez acostado)": request.POST.get("induccion_dormir"),
                "Despertares durante la noche": request.POST.get("despertares_noche"),
                "Despertar final más temprano de lo deseado": request.POST.get("despertar_temprano"),
                "Duración total del dormir": request.POST.get("duracion_dormir"),
                "Calidad general del dormir (no importa cuánto tiempo durmió usted)": request.POST.get("calidad_dormir"),
                "Sensación de bienestar durante el día": request.POST.get("bienestar_dia"),
                "Funcionamiento (físico y mental) durante el día": request.POST.get("funcionamiento_dia"),
                "Somnolencia durante el día": request.POST.get("somnolencia_dia"),
            },
            "ISI":{
                "dificultad_dormir": request.POST.get("dificultad_dormir"),
                "dificultad_mantener_sueno": request.POST.get("dificultad_mantener_sueno"),
                "despertar_temprano": request.POST.get("despertar_temprano"),
                "satisfaccion_sueno": request.POST.get("satisfaccion_sueno"),
                "notabilidad_problema": request.POST.get("notabilidad_problema"),
                "preocupacion_sueno": request.POST.get("preocupacion_sueno"),
                "interferencia_sueno": request.POST.get("interferencia_sueno"),
            }
        }

         # Obtener la visita y el examen correspondiente
        visita_id = request.POST.get('visita_id')
        examen_id = request.POST.get('examen_id')
        # Obtener las instancias de Visita y Examen
        visita = get_object_or_404(Visita, id=visita_id)
        examen = get_object_or_404(Examen, id=examen_id)
        
        paciente_id = request.POST.get('paciente_id') 
        paciente = get_object_or_404(DatosDemograficos, id=paciente_id)
        documento_paciente = paciente.id
        
        # Obtener o crear el VisitaExamen con la relación correcta
        visita_examen, created = VisitaExamen.objects.get_or_create(
            visita=visita, examen=examen
        )

        # Si ya tiene un resultado, lo actualizamos
        if visita_examen.resultado:
            visita_examen.resultado.update(datos_formulario_Cuestionarios)
        else:
            visita_examen.resultado = datos_formulario_Cuestionarios

        # Guardar cambios
        visita_examen.save()

        return redirect(reverse('detalle_paciente', args=[int(documento_paciente)]))
    
@login_required
def descargar_examen(request, visita_examen_id):
    # Obtener el objeto VisitaExamen
    visita_examen = get_object_or_404(VisitaExamen, id=visita_examen_id)
    
    # Obtener los resultados del examen desde ResultadoExamen
    resultado_examen = ResultadoExamen.objects.filter(visita_examen=visita_examen).first()
    
    if not resultado_examen or not resultado_examen.resultado:
        return HttpResponse("No hay resultados para este examen.", status=404)
    
    resultados = resultado_examen.resultado  # Esto es el JSON con los datos del examen

    # Renderizar el HTML con los datos
    html_string = render_to_string('sleepexams/examen_pdf.html', {
        'visita_examen': visita_examen,
        'resultados': resultados,  # Pasamos el JSON a la plantilla
    })

    # Crear un objeto HTML de WeasyPrint
    #html = HTML(string=html_string)
    
    # Generar el PDF
    pdf = html.write_pdf()

    # Devolver el PDF como una respuesta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="examen_{visita_examen.id}.pdf"'
    return response

def profile_view(request):
    return render(request, 'home/profile.html')