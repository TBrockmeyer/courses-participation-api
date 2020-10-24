from django.db import models

class Course(models.Model):
    course_id = models.AutoField(unique=True, primary_key=True)
    course_title = models.CharField(max_length=100, blank=True, default='')
    
    def save(self, *args, **kwargs):
        super(Course, self).save(*args, **kwargs)
