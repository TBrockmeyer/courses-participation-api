from django.db import models

class Course(models.Model):
    course_id = models.AutoField(unique=True, primary_key=True)
    course_title = models.CharField(max_length=100, blank=True, default='')
    participations = models.CharField(max_length=100, blank=True, default='')
    
    def save(self, *args, **kwargs):
        super(Course, self).save(*args, **kwargs)


class Participation(models.Model):
    participation_id = models.AutoField(unique=True, primary_key=True)
    participation_course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(Participation, self).save(*args, **kwargs)
