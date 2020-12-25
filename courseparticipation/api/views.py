from django.core.wsgi import get_wsgi_application
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courseparticipation.settings')

application = get_wsgi_application()

from django.conf import settings
if not settings.configured:
    settings.configure()

from api.models import Course, Participation
from rest_framework import generics, status, exceptions

from api.serializers import CourseSerializer, UserSerializer, ParticipationSerializer
from api.update_db_entries import DbEntriesUpdate

# https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
from rest_framework.response import Response

from django.contrib.auth.models import User

from api.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin

from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly

from django.utils import timezone, dateformat

import datetime

# TODO: 5 [General - imple] check if all classes are compatible with UI, i.e. if there's a button "create" or "destroy" if applicable. Otherwise change & rewrite view types
# TODO: 6 [General - imple] create a Heroku / etc. instance of this API
# TODO: 7 [General - imple] create a cover page that explains login variants, and behind the login wall: links to the pages where objects can be viewed / created / destroyed
# TODO: [UCT - imple] write an endpoint to retrieve the course_runtime_formatted
# TODO: [UCT - imple] write an endpoint to create users

class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]

    """
    List a queryset. (Overridden from rest_framework/mixins.py)
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        # Update the course_runtime information
        db_entries_update = DbEntriesUpdate()
        course_id_list = []
        for item in list(Course.objects.all().values()):
            course_id_list.append(item['course_id'])
        db_entries_update.update_course_time(course_id_list, False)

        return Response(serializer.data)

    def perform_create(self, serializer):
        # Owner may be defined e.g. through serializer.save(owner=self.request.user)
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CourseDeletionByAdmin(generics.DestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminUser]
    

# Add classes for the User models defined in django.contrib.auth.models
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ParticipationCreation(generics.CreateAPIView):
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [IsOwnerOrAdmin]

    # Users call this endpoint indicating a participation_course_id and a participation_course_phase.
    """
    Check given user_id: does have existing participation?
    ├─ No ► Create new participation with requested user_id, course_id and course_phase
    └─ Yes ► Is requested course_phase same as that of existing participation?
        ├─ No ► Refuse request with error  and inform in response that old participation needs to be deleted first
        └─ Yes ► Is requested course_phase adjoining step to that of existing participation?
            ├─ No ► Refuse request with error  and inform in response that only jumps to adjoining phases allowed
            └─ Yes ► update info in database by saving data from request through serializer
    """
    def get_relevant_user_id(self):
        relevant_user_id = self.request.user.id
        if ('user_id' in self.request.data):
            relevant_user_id=int(self.request.data['user_id'])
        return relevant_user_id

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        existing_participation = Participation.objects.filter(user_id=self.get_relevant_user_id())
        relevant_course_id = request.data['participation_course_id']

        relevant_course = Course.objects.filter(course_id=relevant_course_id)
        relevant_course_phases = eval(relevant_course.values()[0]['course_phases'])
        relevant_course_phases_timed = eval(relevant_course.values()[0]['course_phases_timed'])
        relevant_course_phases_nontimed = eval(relevant_course.values()[0]['course_phases_nontimed'])

        requested_course_phase = int(request.data['participation_course_phase'])
        try:
            requested_course_phase_name = relevant_course_phases[requested_course_phase]
        except:
            # Ensure that the requested course phase is within the range of available course phases
            message_valid_course_phases = ""
            for i in range(0, len(relevant_course_phases)):
                message_valid_course_phases += str(i) + ": '" + relevant_course_phases[i] + ("', " if i != len(relevant_course_phases)-1 else "'. ")
            message_course_phase_invalid_value = "The requested course phase is not one of the available phases: " + \
                message_valid_course_phases + \
                "Provide one of the integer numbers, e.g. participation_course_phase=0 for phase " + \
                "'" + relevant_course_phases[0] + "'"
            if (int(request.data['participation_course_phase']) not in [p for p in range(0, len(relevant_course_phases))]):
                raise exceptions.ValidationError(detail=message_course_phase_invalid_value)

        # Ensure that only one participation may exist per user
        if (existing_participation.count() > 0):
            message = "A Participation for this user_id already exists. Delete unwanted participation first by calling participations/delete/."
            raise exceptions.ValidationError(detail=message)

        # Create the participation
        self.perform_create(serializer)

        # Update the course_runtime information
        db_entries_update = DbEntriesUpdate()
        course_id_list = [relevant_course_id]
        # If user changes from timed to nontimed phase, request reset_runtime (will be followed if no other users in timed)
        if(
            (requested_course_phase_name in relevant_course_phases_timed)
        ):
            db_entries_update.update_course_time(course_id_list, True)
        else:
            db_entries_update.update_course_time(course_id_list, False)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user_id=self.get_relevant_user_id())


class ParticipationUpdate(generics.UpdateAPIView):
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [IsOwnerOrAdmin]

    # Users call this endpoint indicating a participation_course_id and a Participation_course_phase.
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        existing_participation = Participation.objects.filter(participation_id=kwargs['pk'])
        existing_participation_course_id = existing_participation.values()[0]['participation_course_id_id']
        existing_participation_course_phase = existing_participation.values()[0]['participation_course_phase']

        relevant_course = Course.objects.filter(course_id=existing_participation_course_id)
        relevant_course_phases = eval(relevant_course.values()[0]['course_phases'])
        relevant_course_phases_timed = eval(relevant_course.values()[0]['course_phases_timed'])
        relevant_course_phases_nontimed = eval(relevant_course.values()[0]['course_phases_nontimed'])

        requested_course_phase = int(request.data['participation_course_phase'])
        try:
            requested_course_phase_name = relevant_course_phases[requested_course_phase]
        except:
            # Ensure that the requested course phase is within the range of available course phases
            message_valid_course_phases = ""
            for i in range(0, len(relevant_course_phases)):
                message_valid_course_phases += str(i) + ": '" + relevant_course_phases[i] + ("', " if i != len(relevant_course_phases)-1 else "'. ")
            message_course_phase_invalid_value = "The requested course phase is not one of the available phases: " + \
                message_valid_course_phases + \
                "Provide one of the integer numbers, e.g. participation_course_phase=0 for phase " + \
                "'" + relevant_course_phases[0] + "'"
            if (int(request.data['participation_course_phase']) not in [p for p in range(0, len(relevant_course_phases))]):
                raise exceptions.ValidationError(detail=message_course_phase_invalid_value)

        existing_participation_course_phase_name = relevant_course_phases[existing_participation_course_phase]

        # Ensure that users may only jump between course phases within one course
        if(int(request.data['participation_course_id']) != existing_participation_course_id):
            # Raise Error
            message = "Users may only jump between phases within one course. If current course shall be exited, delete unwanted participation first by calling participations/delete/."
            raise exceptions.ValidationError(detail=message)

        self.perform_update(serializer)

        # Call runtime update, ONLY with reset_runtime=True IF phase before was nontimed, and new phase is timed.
        course_id_list = [existing_participation_course_id]
        db_entries_update = DbEntriesUpdate()
        # If user changes from timed to nontimed phase, request reset_runtime (will be followed if no other users in timed)
        if(
            (requested_course_phase_name in relevant_course_phases_timed and existing_participation_course_phase_name in relevant_course_phases_nontimed)
        ):
            db_entries_update.update_course_time(course_id_list, True)
        # Otherwise, do not request reset_runtime
        else:
            db_entries_update.update_course_time(course_id_list, False)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ParticipationDeletion(generics.DestroyAPIView):
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_object(self, request):
        """
        Returns the object the view is displaying.
        """
        # Ensure that returned object belongs to requesting user
        queryset = Participation.objects.filter(user_id=request.user.id)

        filter_kwargs = {}
        obj = generics.get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    """
    Destroy a model instance. (Overridden from rest_framework/mixins.py)
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object(self.request)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ParticipationDeletionByAdmin(generics.DestroyAPIView):
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [IsAdminUser]

    def get_object(self, request):
        """
        Returns the object the view is displaying.
        """
        # Ensure that returned object belongs to user in request
        try:
            queryset = Participation.objects.filter(user_id=request.data['user_id'])
        except KeyError:
            message_user_id_required = "Please provide the user_id relevant for the participation to your request, e.g. user_id=1"
            raise exceptions.ValidationError(detail=message_user_id_required)

        filter_kwargs = {}
        obj = generics.get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    """
    Destroy a model instance. (Overridden from rest_framework/mixins.py)
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object(self.request)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ParticipationList(generics.ListAPIView):
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [IsOwnerOrAdmin]

    """
    List a queryset. (Overridden from rest_framework/mixins.py)
    """

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        requesting_user_id = list(User.objects.filter(username=request.user).values())[0]['id']
        if(not request.user.is_superuser or not request.user.is_staff):
            queryset = queryset.filter(user_id=requesting_user_id)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


    """
    Concrete view for listing a queryset.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
