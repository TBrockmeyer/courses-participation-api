# Generated by Django 3.0.7 on 2020-12-17 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20201214_0028'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_runtime_formatted',
            field=models.CharField(blank=True, default='00:00', max_length=50),
        ),
        migrations.AlterField(
            model_name='course',
            name='course_starttime',
            field=models.DateTimeField(default='2020-12-17 23:46:50'),
        ),
    ]
