# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User


class Doctor(models.Model):
    idDoctor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=45)
    correo = models.EmailField(max_length=45, unique=True)
    contraseña = models.CharField(max_length=45)

    def __str__(self):
        return self.nombre