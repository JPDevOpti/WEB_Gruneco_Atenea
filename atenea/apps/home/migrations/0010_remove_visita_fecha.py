# Generated by Django 3.2.6 on 2025-03-10 00:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_auto_20250302_1846'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visita',
            name='fecha',
        ),
    ]
