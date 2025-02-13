# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Proyecto,DatosDemograficos

admin.site.register(Proyecto)
admin.site.register(DatosDemograficos)
# Register your models here.
