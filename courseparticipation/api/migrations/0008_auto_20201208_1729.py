# Generated by Django 3.0.7 on 2020-12-08 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20201115_1257'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_phases',
            field=models.CharField(blank=True, default="['Lobby']", max_length=500),
        ),
        migrations.AlterField(
            model_name='participation',
            name='participation_id',
            field=models.AutoField(primary_key=True, serialize=False, unique=True),
        ),
    ]
