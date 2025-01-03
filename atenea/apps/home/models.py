# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    # Campos adicionales
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    # Sobrescribir las relaciones con related_name personalizado
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )

    def __str__(self):
        return self.username

class Doctor(models.Model):
    idDoctor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=45)
    correo = models.EmailField(max_length=45, unique=True)
    contraseña = models.CharField(max_length=45)

    def __str__(self):
        return self.nombre