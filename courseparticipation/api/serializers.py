from rest_framework import serializers
from api.models import Course

from django.contrib.auth.models import User

class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ['course_id', 'course_title']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'last_login']