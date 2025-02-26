# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.db import models
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
    
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    # Campos Obligatorios
    primer_nombre = models.CharField(max_length=100, verbose_name="Primer Nombre",default=" ")
    segundo_nombre = models.CharField(max_length=100, blank=True, null=True, verbose_name="Segundo Nombre",default=" ")
    primer_apellido = models.CharField(max_length=100, verbose_name="Primer Apellido",default=" ")
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True, verbose_name="Segundo Apellido",default=" ")
    numero_documento = models.CharField(max_length=20, unique=True, verbose_name="Número de Documento",default=" ")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    edad = models.IntegerField(verbose_name="Edad")
    rh = models.CharField(max_length=5, verbose_name="RH",default=" ")
    correo = models.EmailField(unique=True, verbose_name="Correo Electrónico",default="sincorreo@example.com")
    celular = models.CharField(max_length=20, verbose_name="Celular",default="0000000000")

    # Datos Personales Opcionales
    lugar_nacimiento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lugar de Nacimiento")
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES, verbose_name="Género",default="O")
    escolaridad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Escolaridad")
    lateralidad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lateralidad")
    estado_civil = models.CharField(max_length=100, blank=True, null=True, verbose_name="Estado Civil")
    ocupacion = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ocupación")
    eps = models.CharField(max_length=100, blank=True, null=True, verbose_name="EPS")
    direccion_residencia = models.CharField(max_length=200, blank=True, null=True, verbose_name="Dirección de Residencia")
    municipio_residencia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Municipio de Residencia")
    departamento_residencia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Departamento de Residencia")
    pais_residencia = models.CharField(max_length=100, blank=True, null=True, verbose_name="País de Residencia")
    grupo_sanguineo = models.CharField(max_length=5, blank=True, null=True, verbose_name="Grupo Sanguíneo")
    religion = models.CharField(max_length=100, blank=True, null=True, verbose_name="Religión")
    numero_hijos = models.IntegerField(blank=True, null=True, verbose_name="Número de Hijos")

    # Datos del Acompañante
    nombre_acompanante = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nombre del Acompañante")
    relacion_acompanante = models.CharField(max_length=100, blank=True, null=True, verbose_name="Relación con el Participante")
    correo_acompanante = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico del Acompañante")
    telefono_acompanante = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono del Acompañante")

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido} - {self.numero_documento}"


    class Meta:
        verbose_name = "Datos Demográficos"
        verbose_name_plural = "Datos Demográficos"

class Proyecto(models.Model):
    nombre = models.CharField(max_length=255, unique=True, verbose_name="Nombre del Proyecto")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción del Proyecto")
    investigador_principal = models.CharField(max_length=255, blank=True, null=True, verbose_name="Investigador Principal")
    codigo_siu = models.CharField(max_length=50, blank=True, null=True, verbose_name="Código SIU")
    fecha_inicio = models.DateField(blank=True, null=True, verbose_name="Fecha de Inicio")
    fecha_financiacion = models.DateField(blank=True, null=True, verbose_name="Fecha de Financiación")
    pacientes = models.ManyToManyField('DatosDemograficos', related_name='proyectos', verbose_name="Pacientes")
    
    def __str__(self):
        return self.nombre
    
class Examen(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Examen")
    descripcion = models.TextField(verbose_name="Descripción del Examen", blank=True, null=True)
    campos = models.JSONField(verbose_name="Campos del Examen", default=list)  # Estructura del formulario

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Examen"
        verbose_name_plural = "Exámenes"
        
class Visita(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre de la Visita")
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='visitas', verbose_name="Proyecto")
    fecha = models.DateField(verbose_name="Fecha de la Visita")
    observaciones = models.TextField(verbose_name="Observaciones", blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.proyecto.nombre}"

class VisitaExamen(models.Model):
    visita = models.ForeignKey(Visita, on_delete=models.CASCADE, related_name="visita_examenes")
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name="examenes_realizados")
    resultado = models.JSONField(verbose_name="Respuestas del Examen")  # Respuestas específicas

    def __str__(self):
        return f"{self.visita.nombre} - {self.examen.nombre}"
