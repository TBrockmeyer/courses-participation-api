# Generated by Django 3.0.7 on 2020-12-22 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20201222_2332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_phases_timed',
            field=models.CharField(blank=True, default="['Warmup', 'Push', 'Cooldown']", max_length=500),
        ),
    ]