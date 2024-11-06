# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
import os
from django.conf import settings


#@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


#@login_required(login_url="/login/")
def pages(request):
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