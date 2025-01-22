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

class DatosDemograficos(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('PS', 'Pasaporte'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('soltero', 'Soltero(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viudo', 'Viudo(a)'),
        ('union_libre', 'Unión Libre'),
    ]
    
    ESCOLARIDAD_CHOICES = [
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
        ('tecnico', 'Técnico'),
        ('universitario', 'Universitario'),
        ('postgrado', 'Postgrado'),
    ]
    
    LATERALIDAD_CHOICES = [
        ('diestro', 'Diestro'),
        ('zurdo', 'Zurdo'),
        ('ambidiestro', 'Ambidiestro'),
    ]
    
    GRUPO_SANGUINEO_CHOICES = [
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]

    # Información Personal
    nombres_apellidos = models.CharField(max_length=200)
    tipo_documento = models.CharField(max_length=2, choices=TIPO_DOCUMENTO_CHOICES)
    numero_documento = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    edad = models.IntegerField()
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES)
    escolaridad = models.CharField(max_length=20, choices=ESCOLARIDAD_CHOICES)
    
    # Información de Contacto y Adicional
    ocupacion = models.CharField(max_length=100)
    eps = models.CharField(max_length=100)
    lateralidad = models.CharField(max_length=20, choices=LATERALIDAD_CHOICES)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    

    # Información Adicional y Evaluación
    grupo_sanguineo = models.CharField(max_length=3, choices=GRUPO_SANGUINEO_CHOICES)
    religion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombres_apellidos} - {self.numero_documento}"

    class Meta:
        verbose_name = "Datos Demográficos"
        verbose_name_plural = "Datos Demográficos"


class Doctor(models.Model):
    idDoctor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=45)
    correo = models.EmailField(max_length=45, unique=True)
    contraseña = models.CharField(max_length=45)

    def __str__(self):
        return self.nombre