from django.db import models

from django.utils import timezone, dateformat

class Course(models.Model):
    course_id = models.AutoField(unique=True, primary_key=True)
    course_title = models.CharField(max_length=100, blank=True, default='')
    course_phases = models.CharField(max_length=500, blank=True, default="['Lobby']")
    course_starttime = models.DateTimeField(default=dateformat.format(timezone.now(), 'Y-m-d H:i:s'))
    course_runtime = models.IntegerField(default=0)
    course_runtime_formatted = models.CharField(max_length=50, blank=True, default="00:00")
    participations = models.CharField(max_length=100, blank=True, default='')
    
    def save(self, *args, **kwargs):
        super(Course, self).save(*args, **kwargs)


class Participation(models.Model):
    participation_id = models.AutoField(unique=True, primary_key=True)
    participation_course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    participation_course_phase = models.IntegerField(default=0)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(Participation, self).save(*args, **kwargs)
