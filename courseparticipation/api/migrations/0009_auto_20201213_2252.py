# Generated by Django 3.0.7 on 2020-12-13 21:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20201208_1729'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_runtime',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='course',
            name='course_starttime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
