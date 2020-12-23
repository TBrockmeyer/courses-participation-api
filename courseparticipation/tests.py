import unittest

from api.views import UserList, CourseList, ParticipationCreation, ParticipationList, ParticipationUpdate, CourseUpdateRuntime
from api.models import Course, Participation

from api.generate_db_entries import DbEntriesCreation

from django.contrib.auth.models import User

from django.core.wsgi import get_wsgi_application
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courseparticipation.settings')

application = get_wsgi_application()

from django.conf import settings
if not settings.configured:
    settings.configure()

from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, APISimpleTestCase, force_authenticate

import time

class TestApi(APITestCase):
    # Helper methods:
    def auth_test_admin(self):
        auth_username_admin = "test_admin"
        auth_password_admin = "test_admin"
        DbEntriesCreation().create_user_admin(auth_username_admin, auth_password_admin)
        return User.objects.get(username=auth_username_admin)

    def auth_test_user(self):
        auth_username_user = "test_user"
        auth_password_user = "test_user"
        DbEntriesCreation().create_user(auth_username_user, auth_password_user, False, False)
        return User.objects.get(username=auth_username_user)

    def create_test_course_response(self, user, course_title, course_phases, course_phases_nontimed, course_phases_timed):
        view = CourseList.as_view()
        factory = APIRequestFactory()
        request = factory.post('', {'course_title': course_title, 'course_phases': course_phases, 'course_phases_nontimed': course_phases_nontimed, 'course_phases_timed': course_phases_timed})
        force_authenticate(request, user=user)
        return view(request)

    def create_test_participation_response(self, user, participation_course_id, participation_course_phase):
        view = ParticipationCreation.as_view()
        factory = APIRequestFactory()
        request = factory.post('', {'participation_course_id': participation_course_id, 'participation_course_phase': participation_course_phase})
        force_authenticate(request, user=user)
        return view(request)

    def get_test_phases(self):
        return "['Lobby Start', 'Welcome', 'Warmup', 'Push', 'Cooldown', 'Goodbye', 'Lobby End']"

    def get_test_phases_nontimed(self):
        return "['Lobby Start', 'Lobby End']"

    def get_test_phases_timed(self):
        return "['Welcome', 'Warmup', 'Push', 'Cooldown', 'Goodbye']"

    def get_test_participation_response(self, user):
        view = ParticipationList.as_view()
        factory = APIRequestFactory()
        request = factory.get('/participations/')
        force_authenticate(request, user=user)
        return view(request)

    def create_test_participation_update_response(self, user, participation_id, participation_course_id, participation_course_phase):
        view = ParticipationUpdate.as_view()
        factory = APIRequestFactory()
        request = factory.put('', {'participation_course_id': participation_course_id, 'participation_course_phase': participation_course_phase})
        force_authenticate(request, user=user)
        return view(request, pk=str(participation_id))

    # Test methods:
    # Test scope: displaying courses list
    def test_course_list(self):
        view = CourseList.as_view()
        factory = APIRequestFactory()
        request = factory.get('/courses/')
        force_authenticate(request, user=self.auth_test_admin())
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test scope: creating users
    def test_user_creation_admin(self):
        view = UserList.as_view()
        factory = APIRequestFactory()
        request = factory.get('/users/')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.auth_test_admin().username, 'test_admin')

    def test_user_creation_10_users_list(self):
        view = UserList.as_view()
        number_users = 10
        DbEntriesCreation().create_user_examples(number_users)
        user_objects_list = list(User.objects.filter(username__startswith="test_user_").all().values())
        factory = APIRequestFactory()
        request = factory.get('/users/')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range (0, number_users):
            self.assertEqual(user_objects_list[i]['username'], 'test_user_'+str(i))

    # Test scope: user permissions
    ## Only allow admins to create courses
    def test_permission_course_creation(self):
        # Course creation by admin should get status code 201
        response = self.create_test_course_response(self.auth_test_admin(), 'Test Course Permission', self.get_test_phases(), self.get_test_phases_nontimed(), self.get_test_phases_timed())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Course creation by any other user should get a 403 error (as defined in exceptions.py of rest_framework)
        response = self.create_test_course_response(self.auth_test_user(), 'Test Course Permission', self.get_test_phases(), self.get_test_phases_nontimed(), self.get_test_phases_timed())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test scope: participations
    ## Only allow users or admins to create course participations
    def test_permission_participation_creation(self):
        # Create test course as reference
        response_course_creation = self.create_test_course_response(self.auth_test_admin(), 'Test Course Participation', self.get_test_phases(), self.get_test_phases_nontimed(), self.get_test_phases_timed())
        # Participation creation by test user should get status code 201
        response = self.create_test_participation_response(self.auth_test_user(), response_course_creation.data['course_id'], 0)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    ## Only allow users or admins to view user-specific course participations
    def test_permission_participation_view(self):
        # Create test course as reference
        response_course_creation = self.create_test_course_response(self.auth_test_admin(), 'Test Course Participation', self.get_test_phases(), self.get_test_phases_nontimed(), self.get_test_phases_timed())
        # Create test user
        test_user = self.auth_test_user()
        # Create test participation
        response_participation_creation = self.create_test_participation_response(test_user, response_course_creation.data['course_id'], 4)
        # Get participation view response
        response = self.get_test_participation_response(test_user)
        # Participation view response by test user should only show one participation
        self.assertEqual(len(response.data), 1)
        # Participation view response by test user should only show participation of this user
        self.assertEqual(response.data[0]['user_id'], test_user.id)

    # Only allow jumps between course phases in participation updates, but not jumps in courses
    def test_participation_update(self):
        # Create test user
        test_admin = self.auth_test_admin()
        # Create test course as reference
        response_course_1_creation = self.create_test_course_response(test_admin, 'Test Course 1 Participation Update', self.get_test_phases(), self.get_test_phases_nontimed(), self.get_test_phases_timed())
        response_course_2_creation = self.create_test_course_response(test_admin, 'Test Course 2 Participation Update', self.get_test_phases(), self.get_test_phases_nontimed(), self.get_test_phases_timed())
        # Create test user
        test_user = self.auth_test_user()
        # Create test participation
        response_participation_creation = self.create_test_participation_response(test_user, response_course_1_creation.data['course_id'], 0)
        # Participation update by test user should succeed if updating course phase only
        response_a = self.create_test_participation_update_response(test_user, response_participation_creation.data['participation_id'], response_course_1_creation.data['course_id'], 1)
        self.assertEqual(response_a.status_code, status.HTTP_200_OK)
        # Participation update by test user should fail if updating course id
        response_b = self.create_test_participation_update_response(test_user, response_participation_creation.data['participation_id'], response_course_2_creation.data['course_id'], 0)
        self.assertEqual(response_b.status_code, status.HTTP_400_BAD_REQUEST)
        # Participation update by test user should fail if updating course id and course phase
        response_c = self.create_test_participation_update_response(test_user, response_participation_creation.data['participation_id'], response_course_2_creation.data['course_id'], 1)
        self.assertEqual(response_c.status_code, status.HTTP_400_BAD_REQUEST)

class TestApiParticipationUpdate(APITestCase):

    # Helper methods:
    def auth_test_admin(self):
        auth_username_admin = "test_admin"
        auth_password_admin = "test_admin"
        DbEntriesCreation().create_user_admin(auth_username_admin, auth_password_admin)
        return User.objects.get(username=auth_username_admin)

    def auth_test_user(self):
        auth_user_unique_string = "test_user_" + str(int(round(time.time() * 1000)))
        auth_username_user = auth_user_unique_string
        auth_password_user = auth_user_unique_string
        DbEntriesCreation().create_user(auth_username_user, auth_password_user, False, False)
        return User.objects.get(username=auth_username_user)

    def create_test_course_response(self, user, course_title, course_phases, course_phases_nontimed, course_phases_timed):
        view = CourseList.as_view()
        factory = APIRequestFactory()
        request = factory.post('', {'course_title': course_title, 'course_phases': course_phases, 'course_phases_nontimed': course_phases_nontimed, 'course_phases_timed': course_phases_timed})
        force_authenticate(request, user=user)
        return view(request)

    def create_test_participation_response(self, user, participation_course_id, participation_course_phase):
        view = ParticipationCreation.as_view()
        factory = APIRequestFactory()
        request = factory.post('', {'participation_course_id': participation_course_id, 'participation_course_phase': participation_course_phase})
        force_authenticate(request, user=user)
        return view(request)

    def create_test_participation_update_response(self, user, participation_id, participation_course_id, participation_course_phase):
        view = ParticipationUpdate.as_view()
        factory = APIRequestFactory()
        request = factory.put('', {'participation_course_id': participation_course_id, 'participation_course_phase': participation_course_phase})
        force_authenticate(request, user=user)
        return view(request, pk=str(participation_id))

    def create_test_course_runtime_update_response(self, user, course_id, course_runtime=-1):
        view = CourseUpdateRuntime.as_view()
        factory = APIRequestFactory()
        request = factory.put('', {'course_id': course_id, 'course_runtime': course_runtime})
        force_authenticate(request, user=user)
        return view(request, pk=str(course_id))

    def get_test_course_response(self, user):
        view = ParticipationList.as_view()
        factory = APIRequestFactory()
        request = factory.get('/courses/')
        force_authenticate(request, user=user)
        return view(request)

    def get_test_phases(self):
        return "['Lobby Start', 'Welcome', 'Warmup', 'Push', 'Cooldown', 'Goodbye', 'Lobby End']"

    def get_test_phases_nontimed(self):
        return "['Lobby Start', 'Lobby End']"

    def get_test_phases_timed(self):
        return "['Welcome', 'Warmup', 'Push', 'Cooldown', 'Goodbye']"

    # Test fixtures
    def setUp(self):
        self.test_admin = self.auth_test_admin()
        self.test_user_1 = self.auth_test_user()
        self.test_user_2 = self.auth_test_user()
        self.test_course = self.create_test_course_response(self.test_admin, 'Test Course Participation', self.get_test_phases(), self.get_test_phases_nontimed(), self.get_test_phases_timed())
        self.test_participation_course_phase_initial = 0
        self.test_participation = self.create_test_participation_response(
            self.test_user_1,
            self.test_course.data['course_id'],
            self.test_participation_course_phase_initial
        )
        self.test_participation_2 = self.create_test_participation_response(
            self.test_user_2,
            self.test_course.data['course_id'],
            self.test_participation_course_phase_initial
        )

    def test_participation_update_first_users(self):
        participation_1_id = self.test_participation.data['participation_id']
        participation_2_id = self.test_participation_2.data['participation_id']
        participation_course_id = self.test_participation.data['participation_course_id']
        participation_course_phase = 1

        # Participation update with
        # ├─ first user entering a lobby phase
        # should
        # ├─ not update course_starttime
        # └─ not update course_runtime
        course_object_values_pre = Course.objects.filter(course_id=participation_course_id).values()[0]
        delay_user_1_entering = 1.0
        time.sleep(delay_user_1_entering)
        response = self.create_test_participation_update_response(self.test_user_1, participation_1_id, participation_course_id, self.test_participation_course_phase_initial)
        course_object_values_post = Course.objects.filter(course_id=participation_course_id).values()[0]

        self.assertEqual(course_object_values_post['course_starttime'], course_object_values_pre['course_starttime'])
        self.assertEqual(course_object_values_post['course_runtime'], 0)

        # Participation update with
        # ├─ first user entering a nonlobby phase
        # should
        # ├─ update course_starttime
        # └─ not update course_runtime
        course_object_values_pre = Course.objects.filter(course_id=participation_course_id).values()[0]
        delay_user_1_entering = 1.0
        time.sleep(delay_user_1_entering)
        response = self.create_test_participation_update_response(self.test_user_1, participation_1_id, participation_course_id, participation_course_phase)
        course_object_values_post = Course.objects.filter(course_id=participation_course_id).values()[0]

        self.assertNotEqual(course_object_values_post['course_starttime'], course_object_values_pre['course_starttime'])
        self.assertEqual(course_object_values_post['course_runtime'], 0)

        # Participation update with
        # ├─ second user entering a nonlobby phase
        # should
        # ├─ not update course_starttime
        # └─ update course_runtime to specified delay_user_2_entering
        delay_user_2_entering = 1.0
        time.sleep(delay_user_2_entering)
        response = self.create_test_participation_update_response(self.test_user_2, participation_2_id, participation_course_id, participation_course_phase)
        course_object_values_post_2 = Course.objects.filter(course_id=participation_course_id).values()[0]
        self.assertEqual(course_object_values_post_2['course_starttime'], course_object_values_post['course_starttime'])
        self.assertEqual(course_object_values_post_2['course_runtime'], delay_user_1_entering + delay_user_2_entering)

        # Participation update with
        # ├─ first user being in a nonlobby phase
        # ├─ second user being in a nonlobby phase
        # ├─ second user entering a lobby phase
        # should
        # ├─ not update course_starttime
        # └─ update course_runtime to specified delay_user_2_entering + delay_user_2_exiting
        delay_user_2_exiting = 1.0
        time.sleep(delay_user_2_exiting)
        response = self.create_test_participation_update_response(self.test_user_2, participation_2_id, participation_course_id, self.test_participation_course_phase_initial)
        course_object_values_post_3 = Course.objects.filter(course_id=participation_course_id).values()[0]
        self.assertEqual(course_object_values_post_3['course_starttime'], course_object_values_post_2['course_starttime'])
        self.assertEqual(course_object_values_post_3['course_runtime'], delay_user_2_entering + delay_user_2_exiting)

        # Participation update with
        # ├─ first user entering a lobby phase
        # should
        # ├─ not update course_starttime
        # └─ update course_runtime to 0
        delay_user_1_exiting = 1.0
        time.sleep(delay_user_1_exiting)
        response = self.create_test_participation_update_response(self.test_user_1, participation_1_id, participation_course_id, self.test_participation_course_phase_initial)
        course_object_values_post_4 = Course.objects.filter(course_id=participation_course_id).values()[0]
        self.assertEqual(course_object_values_post_4['course_starttime'], course_object_values_post_3['course_starttime'])
        self.assertEqual(course_object_values_post_4['course_runtime'], 0)


if __name__ == '__main__':
    unittest.main()
