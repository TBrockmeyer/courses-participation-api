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
from api.generate_db_entries import DbEntriesCreation

# https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
from rest_framework.response import Response

from django.contrib.auth.models import User

from api.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin

from rest_framework.permissions import IsAdminUser

# TODO: check if all classes are compatible with UI, i.e. if there's a button "create" or "destroy" if applicable. Otherwise change & rewrite view types

class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]

    # TODO: add timer field to courses and update it depending on users entering the course / the lobby phase

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

    # Users call this endpoint indicating a participation_course_id and a Participation_course_phase.
    # TODO: ensure that the Course objects are aware of their participations (e.g. through dicts or json)
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

        # Ensure that only one participation may exist per user
        if (existing_participation.count() > 0):
            message = "A Participation for this user_id already exists. Delete unwanted participation first by calling participations/delete/."
            raise exceptions.ValidationError(detail=message)

        # Ensure that the requested course phase is within the range of available course phases
        requested_course = Course.objects.filter(course_id=request.data['participation_course_id'])
        requested_course_phases = eval(requested_course.values()[0]['course_phases'])
        message_valid_course_phases = ""
        for i in range(0, len(requested_course_phases)):
            message_valid_course_phases += str(i) + ": '" + requested_course_phases[i] + ("', " if i != len(requested_course_phases)-1 else "'. ")
        message_course_phase_invalid_value = "The requested course phase is not one of the available phases: " + \
            message_valid_course_phases + \
            "Provide one of the integer numbers, e.g. participation_course_phase=0 for phase " + \
            "'" + requested_course_phases[0] + "'"
        if (int(request.data['participation_course_phase']) not in [p for p in range(0, len(requested_course_phases))]):
            raise exceptions.ValidationError(detail=message_course_phase_invalid_value)

        # Create the participation
        self.perform_create(serializer)
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

        # Ensure that users may only jump between course phases within one course
        if(int(request.data['participation_course_id']) != existing_participation_course_id):
            # Raise Error
            message = "Users may only jump between phases within one course. If current course shall be exited, delete unwanted participation first by calling participations/delete/."
            raise exceptions.ValidationError(detail=message)

        self.perform_update(serializer)

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
        # Ensure that returned object belongs to requesting user
        queryset = Participation.objects.filter(user_id=request.data['user_id'])

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
    List a queryset.
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
