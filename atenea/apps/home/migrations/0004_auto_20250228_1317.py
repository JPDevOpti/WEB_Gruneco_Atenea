# Generated by Django 3.2.6 on 2025-02-28 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20250224_1727'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datosdemograficos',
            options={},
        ),
        migrations.RemoveField(
            model_name='datosdemograficos',
            name='celular',
        ),
        migrations.RemoveField(
            model_name='datosdemograficos',
            name='correo',
        ),
        migrations.RemoveField(
            model_name='datosdemograficos',
            name='correo_acompanante',
        ),
        migrations.RemoveField(
            model_name='datosdemograficos',
            name='direccion_residencia',
        ),
        migrations.RemoveField(
            model_name='datosdemograficos',
            name='grupo_sanguineo',
        ),
        migrations.RemoveField(
            model_name='datosdemograficos',
            name='lugar_nacimiento',
        ),
        migrations.RemoveField(
            model_name='datosdemograficos',
            name='nombre_acompanante',
        ),
        migrations.RemoveField(
            model_name='datosdemograficos',
            name='numero_hijos',
        ),
        migrations.RemoveField(
            model_name='datosdemograficos',
            name='relacion_acompanante',
        ),
        migrations.RemoveField(
            model_name='datosdemograficos',
            name='rh',
        ),
        migrations.RemoveField(
            model_name='datosdemograficos',
            name='telefono_acompanante',
        ),
        migrations.AddField(
            model_name='datosdemograficos',
            name='departamento_nacimiento',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='datosdemograficos',
            name='direccion',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='datosdemograficos',
            name='municipio_nacimiento',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='datosdemograficos',
            name='pais_nacimiento',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='datosdemograficos',
            name='regimen',
            field=models.CharField(choices=[('Contributivo', 'Contributivo'), ('Subsidiado', 'Subsidiado'), ('Vinculado', 'Vinculado'), ('Otro', 'Otro')], default='', max_length=20),
        ),
        migrations.AddField(
            model_name='datosdemograficos',
            name='tipo_documento',
            field=models.CharField(choices=[('CC', 'Cédula de Ciudadanía'), ('TI', 'Tarjeta de Identidad'), ('NUIP', 'Número Único de Identificación Personal'), ('CE', 'Cédula de Extranjería'), ('PS', 'Pasaporte')], default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='departamento_residencia',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='edad',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='eps',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='escolaridad',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='estado_civil',
            field=models.CharField(choices=[('Soltero', 'Soltero(a)'), ('Casado', 'Casado(a)'), ('UnionLibre', 'Unión libre'), ('Viudo', 'Viudo(a)')], max_length=20),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='fecha_nacimiento',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='genero',
            field=models.CharField(choices=[('F', 'Femenino'), ('M', 'Masculino'), ('O', 'Otro')], max_length=10),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='lateralidad',
            field=models.CharField(choices=[('Diestro', 'Diestro'), ('Zurdo', 'Zurdo'), ('Ambidiestro', 'Ambidiestro')], max_length=20),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='municipio_residencia',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='numero_documento',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='ocupacion',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='pais_residencia',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='primer_apellido',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='primer_nombre',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='religion',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='segundo_apellido',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='datosdemograficos',
            name='segundo_nombre',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
