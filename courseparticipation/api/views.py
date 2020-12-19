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

from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly

from django.utils import timezone, dateformat

import datetime

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


class CourseUpdateRuntime(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # TODO: Write test cases for all possible combinations of users distributed over the course phases (lobby / non-lobby / no users at all)
    # and for each combination, all possible transitions (from lobby to non-lobby, directly into non-lobby, directly from non-lobby out (harsh exit / kicked))
    # TODO: call class CourseUpdateRuntime whenever a transition is happening
    # TODO: write an endpoint to retrieve the course_runtime_formatted

    """
    Re-calculate passed days, hours, minutes, seconds from given seconds
    Adapted from: https://stackoverflow.com/questions/4048651/python-function-to-convert-seconds-into-minutes-hours-and-days
    """

    def display_time(self, seconds, granularity=2):
        self.intervals = (
            ('days', 86400),    # 60 * 60 * 24
            ('hours', 3600),    # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
        )

        result = []

        granularity = 3 if seconds >= 3600 else granularity
        granularity = 4 if seconds >= 86400 else granularity

        for _, count in self.intervals:
            value = seconds // count
            seconds -= value * count
            result.append("{}".format(value).zfill(2))
        return ':'.join(result[-granularity:])

    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        requested_runtime = -1
        try:
            requested_runtime = int(request.data['course_runtime'])
        except:
            pass

        relevant_course_id = instance.course_id
        existing_course_values = list(Course.objects.filter(course_id=relevant_course_id).values())[0]
        existing_course_phase_max = len(eval(existing_course_values['course_phases'])) - 1

        number_users_lobby_start = int(len(list(Participation.objects.filter(participation_course_id=relevant_course_id, participation_course_phase=0).values())))
        number_users_lobby_end = int(len(list(Participation.objects.filter(participation_course_id=relevant_course_id, participation_course_phase=existing_course_phase_max).values())))
        number_users_course = int(len(list(Participation.objects.filter(participation_course_id=relevant_course_id).values())))
        number_users_lobby = number_users_lobby_start + number_users_lobby_end
        number_users_nonlobby = number_users_course - number_users_lobby
        number_users_phase_first_timed = int(len(list(Participation.objects.filter(participation_course_id=relevant_course_id, participation_course_phase=1).values())))

        existing_course_runtime = existing_course_values['course_runtime']
        existing_course_starttime = existing_course_values['course_starttime']

        date_format_datetime = '%Y-%m-%d %H:%M:%S'
        date_format_datetime_seconds = '%S'
        date_format_timezone = 'Y-m-d H:i:s'

        if(number_users_phase_first_timed == 1 and number_users_nonlobby == 1 and int(requested_runtime) == 0):
            # "There is exactly one user inside the first timed phase of the course, and the requested course_runtime is 0"
            # Whenever a user switches from phase 0 ('Lobby Start') to phase 1 ('Warmup'),
            # the update call tries to indicate that this is a "time 0" call,
            # i.e. that it's the first user entering and thus starting the course.
            # We follow this indication only if there are no other users anywhere in the course,
            # except for the first lobby phase ('Lobby Start').
            # Set course_starttime to now.
            # Set course-runtime to 0.
            current_time = dateformat.format(timezone.now(), date_format_timezone)
            request.data['course_starttime'] = current_time
            request.data['course_runtime'] = 0
            request.data['course_runtime_formatted'] = self.display_time(request.data['course_runtime'])

        elif(number_users_nonlobby == 0):
            # "There are no users in the non-lobby phases of the course"
            # This describes e.g. the cases where
            # ├─ a list of the courses is requested, and no user is inside the course
            # └─ the last user just left the course
            # Set course_starttime to 0000-00-00T00:00:00Z
            # Set course_runtime to 0
            request.data['course_starttime'] = "0001-01-01T00:00:00Z"
            request.data['course_runtime'] = 0
            request.data['course_runtime_formatted'] = self.display_time(request.data['course_runtime'])

        else:
            # "There are already/still users in the non-lobby phases of the course, and the requested course_runtime is not 0"
            # Set course_starttime to existing course_starttime
            # Set (update) course_runtime to timediff between now and course_starttime
            current_time = datetime.datetime.strptime(dateformat.format(timezone.now(), date_format_timezone), date_format_datetime)
            course_starttime = datetime.datetime.strptime(datetime.datetime.strftime(existing_course_starttime, date_format_datetime), date_format_datetime)
            timediff = int((current_time - course_starttime).total_seconds())
            request.data['course_starttime'] = existing_course_starttime
            request.data['course_runtime'] = timediff
            request.data['course_runtime_formatted'] = self.display_time(request.data['course_runtime'])


        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
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
