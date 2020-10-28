from django.core.wsgi import get_wsgi_application
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courseparticipation.settings')

application = get_wsgi_application()

from django.conf import settings
if not settings.configured:
    settings.configure()

from api.models import Course, Participation
from rest_framework import generics, status

from api.serializers import CourseSerializer, UserSerializer, ParticipationSerializer
from api.generate_db_entries import DbEntriesCreation

# https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
from rest_framework.response import Response

from django.contrib.auth.models import User

from api.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin

class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        # Owner can be defined e.g. through serializer.save(owner=self.request.user)
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

# Add classes for the User models defined in django.contrib.auth.models
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ParticipationList(generics.ListCreateAPIView):
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_create(self, serializer):
        # Users call this endpoint indicating a participation_course_id and a Participation_course_phase.

        # TODO: If user is admin, check if relevant user id is given. Else, throw error.
        # TODO: If no participation exists for user, create participation
        # TODO critical: go through the case that a user_id is far outside the max!
        if ('user_id' in self.request.data):
            serializer.save(user_id=int(self.request.data['user_id']))
        else:
            serializer.save(user_id=self.request.user.id)

class ParticipationUpdate(generics.RetrieveUpdateAPIView):
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_create(self, serializer):
        # Users call this endpoint indicating a participation_course_id and a Participation_course_phase.

        # TODO: If user is admin, check if relevant user id is given. Else, throw error.
        # TODO: If no participation exists for user, create participation
        participation_object = Participation.objects.filter(user_id=self.request.user.id)
        #serializer.save(user_id=self.request.user.id)
        serializer.save(user_id=int(self.request.data['user_id']))

        # TODO: If requested course is the same as before, and user requests to do an allowed switch of phases:
        ## Delete existing Participation database entry
        ## Create new Participation entry with new phase information

        # TODO: If user attempts to switch course without having deleted an existing Participation before, throw error:
        ## Appropriate error to remind user to exit their other course first
        ## Optional: printed error message why the request was denied


class ParticipationDeletion(generics.RetrieveUpdateAPIView):
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_create(self, serializer):
        Participation.objects.filter(user_id=self.request.user.id).delete()
