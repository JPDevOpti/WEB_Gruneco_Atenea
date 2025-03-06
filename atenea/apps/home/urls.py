# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from apps.home import views
from .views import login_view, descargar_examen, profile_view

urlpatterns = [
    # Páginas principales
    path('', views.home, name='home'),  # Página de inicio gruneco.com.co
    path('index/', views.index, name='index'),  # Página de inicio de Atenea
    path('login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),  # Perfil de usuario

    # Registro de pacientes
    path('registro-demografico/', views.registro_demografico, name='registro_demografico'),
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('paciente/<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),
    path('paciente/<int:numero_documento>/eliminar/', views.eliminar_paciente, name='eliminar_paciente'),
    path('paciente/<int:numero_documento>/editar/', views.editar_paciente, name='editar_paciente'),

    # Exámenes médicos
    path('descargar-examen/<int:visita_examen_id>/', descargar_examen, name='descargar_examen'),
    path('examen/<int:visita_id>/<int:examen_id>/<int:paciente_id>/', views.realizar_examen, name='realizar_examen'),
    path('guardar-examen/general/', views.guardar_examen_general_revisionsistemas, name='guardar_examen_general'),
    path('guardar-examen/fisico/', views.guardar_examen_fisico, name='guardar_examen_fisico'),
    path('guardar-examen/antecedentes/', views.guardar_examen_antecedentes, name='guardar_examen_antecedentes'),

    # Proyectos
    path('proyectos/', views.proyectos, name='proyectos'),
    path('proyecto/agregar-visita/', views.agregar_visita, name='agregar_visita'),
    path('proyecto/<int:id>/eliminar/', views.eliminar_proyecto, name='eliminar_proyecto'),

    # Estadísticas
    path('estadisticas/', views.estadisticas, name='estadisticas'),
]
