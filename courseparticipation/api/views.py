#from django.shortcuts import render

from api.models import Course
from rest_framework import generics

from api.serializers import CourseSerializer

class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    # TODO: create test in TestApi.py