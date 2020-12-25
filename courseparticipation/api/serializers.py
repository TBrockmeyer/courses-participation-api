from rest_framework import serializers
from api.models import Course, Participation

from django.contrib.auth.models import User

class ParticipationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participation
        fields = ['participation_id', 'participation_course_id', 'participation_course_phase', 'user_id']


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ['course_id', 'course_title', 'course_phases', 'course_phases_timed', 'course_phases_nontimed', 'course_starttime', 'course_runtime', 'course_runtime_formatted']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'last_login']
