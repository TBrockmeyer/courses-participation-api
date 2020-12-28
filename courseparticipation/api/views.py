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

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView

from django.utils import timezone, dateformat

import datetime

import hashlib

# TODO: 8 [General - imple] create a cover page that explains login variants, default field values


class UrlList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'url_list.html'

    def get(self, request):
        description_admin_login = "Go to the login URL and login with the credentials provided by your contact via email."
        example_admin_login = "username: admin_2021 [valid value provided in personal message]\npassword: admin_2021 [valid value provided in personal message]"
        description_course_creation = "Create courses with course title and the timed and non-timed phases of the course ('non-timed' meaning: the timer is halted if all course participants are only in a non-timed phase).\nPlease find an example how to define the course phases below. Open the URL, enter the example details and click the 'POST' button to create the new course. You can leave the course_runtime fields empty or fill them; please note that they will only be updated as soon as users start participating in the course (handled further below)."
        example_course_creation = "Course title: Course 5\nCourse phases: ['Lobby Start', 'Welcome', 'Push', 'Lobby End']\nCourse phases timed: ['Welcome', 'Push']\nCourse phases nontimed: ['Lobby Start', 'Lobby End']"
        description_course_list_admin = "View a list of all courses."
        example_course_list_admin = False
        description_course_deletion = "Delete one of the courses you just created (or any other course you don't want to keep). Determine the course_id of your course with the course list endpoint introduced above, and replace the '2' in the URL with it. After opening the URL, click the 'DELETE' button to actually delete the course."
        example_course_deletion = False
        description_user_list = "View a list of all users."
        example_user_list = False
        description_user_creation = "Create new users. For this demo, the password will be the same as the username you're entering. Open the URL, enter the example details and click the 'POST' button to create the new user."
        example_user_creation = "Username: user_6\n(Password [will be set automatically, doesn\'t have a UI field]: user_6)"
        description_user_login = "Log out, and login again as a normal user, e.g. with the credentials from the example, or any other user. Users user_2 to user_5 have been pre-created."
        example_user_login = "Username: user_2\nPassword: user_2"
        description_course_list_user = "View all courses and the available phases. For the step below, remember already now the course_id (e.g. '3') of the course you'd like to participate in, and the index of a timed phase in the list of all phases of the course; e.g. remember '2' if the timed phases are ['Welcome', 'Push'] and all phases are ['Lobby Start', 'Welcome', 'Push', 'Lobby End'].\nWhy is '2' a valid index of a timed phase? Because 'Push' is in position 2 among the indices of all course phases (0: 'Lobby Start', 1: 'Welcome', 2: 'Push', 3: 'Lobby End'), and phase 2: 'Push' is a timed phase."
        example_course_list_user = False
        description_participation_creation = "Create a course participation for the logged-in user. Provide the course_id of the course you want to enter (e.g. '3'), and provide the index of a timed participation (e.g. '2') so that course timers start. Open the URL, enter the example details and click the 'POST' button to create the new participation."
        example_participation_creation = "Participation course id: Course object (3) [this is the course with the course ID 3]\nParticipation course phase: 2 [or the index of any timed phase you remembered from the course]"
        description_course_list_timer = "Wait a few seconds. Then open URL and view all courses. Note that the course_runtime and course_runtime_formatted for the course you're participating in now also show some seconds passed. Reload page to verify (course_runtime_formatted always updated to its current number of seconds runtime)."
        example_course_list_timer = "{\"course_id\": 3,\n\"course_title\": \"Course 3\",\n\"course_phases\": \"['Lobby Start', 'Welcome', 'Push', 'Lobby End']\",\n\"course_phases_timed\": \"['Welcome', 'Push']\",\n\"course_phases_nontimed\": \"['Lobby Start', 'Lobby End']\",\n\"course_starttime\": \"2021-01-03T13:43:38.539444Z\",\n\"course_runtime\": 10,\n\"course_runtime_formatted\": \"00:10\"}"
        description_participation_list = "View your existing participation. Empty if no participation created yet. Remember your participation_id if available."
        example_participation_list = False
        description_participation_update = "Update your participation (replace '1' in the URL by your participation_id if necessary). For participation_course_phase, enter the index of a non-timed phase (e.g. '0')."
        example_participation_update = "Participation course phase: 0"
        description_course_list_timer_paused = "View all courses. Note that the course_runtime and course_runtime_formatted for the course you're participating in now show a paused timer. Reload page to verify (course_runtime_formatted persists at its paused number of seconds runtime)."
        example_course_list_timer_paused = False
        description_participation_deletion_user = "Delete your participation in the course. Open the URL, and click on the red button 'DELETE' to delete it. View your participations again to verify that it has been deleted."
        example_participation_deletion_user = False
        description_admin_login_2 = "Logout, go to the login URL and login again with the credentials provided by your contact via email."
        example_admin_login_2 = "username: admin_2021 [valid value provided in personal message]\npassword: admin_2021 [valid value provided in personal message]"
        description_participation_deletion_admin = "Would you like to remove a user from the course? View all participations. Go to admin delete URL listed below. Delete e.g. participation with participation_id 2 (or replace '2' with any other valid participation_id)."
        example_participation_deletion_admin = "Participation id: 2"
        description_step_iteration = "Go through the steps above again to create more users, courses, participations... and delete them again, and check the impact of these actions on course runtimes.\nIn the GitHub project, the logic behind the course runtime updates can be found inside class 'courseparticipation/api/update_db_entries.py', in the method 'update_course_time()'."
        example_step_iteration = False

        base_url = "https://course-participation-api.herokuapp.com/"
        url_dict = [
            {'title': 'Admin login', 'description': description_admin_login, 'url': base_url + 'api-auth/login/?next=/courses/', 'example': example_admin_login},
            {'title': 'Course creation', 'description': description_course_creation, 'url': base_url + 'courses/', 'example': example_course_creation},
            {'title': 'Course list', 'description': description_course_list_admin, 'url': base_url + 'courses/', 'example': example_course_list_admin},
            {'title': 'Course deletion by logged-in admin', 'description': description_course_deletion, 'url': base_url + 'courses/admindelete/2/', 'example': example_course_deletion},
            {'title': 'Users list', 'description': description_user_list, 'url': base_url + 'users/', 'example': example_user_list},
            {'title': 'User creation', 'description': description_user_creation, 'url': base_url + 'users/', 'example': example_user_creation},
            {'title': 'User login', 'description': description_user_login, 'url': base_url + 'api-auth/login/?next=/courses/', 'example': example_user_login},
            {'title': 'Course list', 'description': description_course_list_user, 'url': base_url + 'courses/', 'example': example_course_list_user},
            {'title': 'Participation creation', 'description': description_participation_creation, 'url': base_url + 'participations/create/', 'example': example_participation_creation},
            {'title': 'Course list', 'description': description_course_list_timer, 'url': base_url + 'courses/', 'example': example_course_list_timer},
            {'title': 'Participation list', 'description': description_participation_list, 'url': base_url + 'participations/', 'example': example_participation_list},
            {'title': 'Participation update', 'description': description_participation_update, 'url': base_url + 'participations/update/1/', 'example': example_participation_update},
            {'title': 'Course list', 'description': description_course_list_timer_paused, 'url': base_url + 'courses/', 'example': example_course_list_timer_paused},
            {'title': 'Participation deletion\n by logged-in user', 'description': description_participation_deletion_user, 'url': base_url + 'participations/delete/', 'example': example_participation_deletion_user},
            {'title': 'Participation creation', 'description': description_participation_creation, 'url': base_url + 'participations/create/', 'example': example_participation_creation},
            {'title': 'Admin login', 'description': description_admin_login_2, 'url': base_url + 'api-auth/login/?next=/courses/', 'example': example_admin_login_2},
            {'title': 'Participation deletion\n by logged-in admin', 'description': description_participation_deletion_admin, 'url': base_url + 'participations/admindelete/2/', 'example': example_participation_deletion_admin},
            {'title': 'Step iteration', 'description': description_step_iteration, 'url': base_url + 'courses/', 'example': example_step_iteration},
        ]
        return Response({'purposes': url_dict})


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
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Delete just created user again
        User.objects.filter(username=request.data['username']).delete()

        if(User.objects.filter(username=request.data['username']).count() > 0):
            raise exceptions.ValidationError(detail="User with requested username already exists.")
        else:
            User.objects.filter(username=request.data['username']).delete()
            user=User.objects.create_user(username=request.data['username'], password=request.data['username'])
            user.is_superuser=False
            user.is_staff=False
            user.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserAdminCreation(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    """
    Create a model instance. (Overridden from rest_framework/mixins.py)
    Usage example: http POST <localhost>/users/create/admin username="admin" password="admin"
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Delete just created user again
        User.objects.filter(username=request.data['username']).delete()

        # If requested username matches expected md5 hash, and this admin user doesn't exist yet,
        # replace now-created admin user by a new admin user with the given password
        allowed_hashes = ["212bd44fe9b6d0cd2b4a7a0431aef17a", "2d83d0b11cbf4bb666928410a22aa6ef"]
        m = hashlib.md5()
        m.update(request.data['username'].encode('utf-8'))
        if(str(m.hexdigest()) in allowed_hashes):
            if(User.objects.filter(username=request.data['username']).count() > 0):
                raise exceptions.ValidationError(detail="Admin user with requested username already exists.")
            else:
                User.objects.filter(username=request.data['username']).delete()
                user=User.objects.create_user(username=request.data['username'], password=request.data['username'])
                user.is_superuser=True
                user.is_staff=True
                user.save()
        else:
            raise exceptions.ValidationError(detail="Admin user with requested username could not be created. Contact project owner to request credentials.")

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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


class ParticipationUpdate(generics.RetrieveUpdateAPIView):
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
