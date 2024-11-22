from django.db import models

class Doctor(models.Model):
    idDoctor = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=45)
    Correo = models.CharField(max_length=45, unique=True)
    Contraseña = models.CharField(max_length=45)

    class Meta:
        db_table = 'Doctors'
