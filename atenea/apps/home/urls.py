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
    
    path('registro_demografico/', views.registro_demografico, name='registro_demografico'),
    path('pacientes/', views.lista_pacientes, name='tables.html'),
    path('paciente/<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),
    path('paciente/<int:numero_documento>/eliminar/', views.eliminar_paciente, name='eliminar_paciente'),
    #path('agregar-proyecto/<int:paciente_id>/', views.agregar_proyecto, name='agregar_proyecto'),
    # Matches any html file
    #re_path(r'^(?!login).*\.*', views.pages, name='pages'),
    
]

