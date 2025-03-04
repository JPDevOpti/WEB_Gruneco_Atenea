# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import login_view

urlpatterns = [

    # The home page
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    #resgistro de pacientes 
    path('registro_demografico/', views.registro_demografico, name='registro_demografico'),
    path('pacientes/', views.lista_pacientes, name='tables.html'),
    path('paciente/<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),
    path('paciente/<int:numero_documento>/eliminar/', views.eliminar_paciente, name='eliminar_paciente'),
    path('editar_paciente/<int:numero_documento>/editar', views.editar_paciente, name='editar_paciente'),

    #examenes
    path('descargar_examen/<int:visita_examen_id>/', views.descargar_examen, name='descargar_examen'),
    path('examen/<int:visita_id>/<int:examen_id>/<int:paciente_id>/', views.realizar_examen, name='realizar_examen'),
    path('guardar-examen-general/', views.guardar_examen_general_revisionsistemas, name='guardar_examen'),
    path('guardar-examen-fisico/', views.guardar_examen_fisico, name='guardar_examen_fisico'),
    path('guardar-examen-antecedentes', views.guardar_examen_antecedentes, name='guardar_examen_antecedentes'),
    
    # Nueva ruta para proyectos
    path('proyectos/', views.proyectos, name='proyectos'),
    path("agregar-visita/", views.agregar_visita, name="agregar_visita"),
    path('proyecto/eliminar/<int:id>/', views.eliminar_proyecto, name='eliminar_proyecto'),

    #estadisticas
    path('estadisticas/', views.estadisticas, name='estadisticas'),

    
]
