import unittest

from api.views import UserList, CourseList, ParticipationCreation, ParticipationList, ParticipationUpdate
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

# TODO: 4 [Tests - refac] rename all test_participation_phase to test_participation_phase_id, and then test_participation_phase_name to test_participation_phase

# Global helper methods
def auth_test_admin():
    auth_username_admin = "test_admin"
    auth_password_admin = "test_admin"
    DbEntriesCreation().create_user_admin(auth_username_admin, auth_password_admin)
    return User.objects.get(username=auth_username_admin)

def auth_test_user():
    auth_user_unique_string = "test_user_" + str(int(round(time.time() * 1000)))
    auth_username_user = auth_user_unique_string
    auth_password_user = auth_user_unique_string
    DbEntriesCreation().create_user(auth_username_user, auth_password_user, False, False)
    return User.objects.get(username=auth_username_user)

def get_test_phases():
    return "['Lobby Start', 'Welcome', 'Warmup', 'Push', 'Cooldown', 'Goodbye', 'Lobby End']"

def get_test_phases_nontimed():
    return "['Lobby Start', 'Lobby End']"

def get_test_phases_timed():
    return "['Welcome', 'Warmup', 'Push', 'Cooldown', 'Goodbye']"

def create_test_course_response(user, course_title, course_phases, course_phases_nontimed, course_phases_timed):
    view = CourseList.as_view()
    factory = APIRequestFactory()
    request = factory.post('', {'course_title': course_title, 'course_phases': course_phases, 'course_phases_nontimed': course_phases_nontimed, 'course_phases_timed': course_phases_timed})
    force_authenticate(request, user=user)
    return view(request)

def create_test_participation_response(user, participation_course_id, participation_course_phase):
    view = ParticipationCreation.as_view()
    factory = APIRequestFactory()
    request = factory.post('', {'participation_course_id': participation_course_id, 'participation_course_phase': participation_course_phase})
    force_authenticate(request, user=user)
    return view(request)

def create_test_participation_update_response(user, participation_id, participation_course_id, participation_course_phase):
    view = ParticipationUpdate.as_view()
    factory = APIRequestFactory()
    request = factory.put('', {'participation_course_id': participation_course_id, 'participation_course_phase': participation_course_phase})
    force_authenticate(request, user=user)
    return view(request, pk=str(participation_id))

def get_test_participation_response(user):
    view = ParticipationList.as_view()
    factory = APIRequestFactory()
    request = factory.get('/participations/')
    force_authenticate(request, user=user)
    return view(request)

def get_test_course_response(user):
    view = CourseList.as_view()
    factory = APIRequestFactory()
    request = factory.get('/courses/')
    force_authenticate(request, user=user)
    return view(request)

class TestApiCoursesList(APITestCase):
    # Helper methods

    # Test fixtures
    def setUp(self):
        self.test_admin = auth_test_admin()

    # Test methods
    # Test scope: displaying courses list
    def test_course_list(self):
        response = get_test_course_response(self.test_admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class TestApiUserCreation(APITestCase):
    # Test fixtures
    def setUp(self):
        self.test_admin = auth_test_admin()

    # Test methods
    def test_user_creation_admin(self):
        view = UserList.as_view()
        factory = APIRequestFactory()
        request = factory.get('/users/')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_admin.username, 'test_admin')

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

class TestApiUserPermission(APITestCase):
    # Test fixtures
    def setUp(self):
        self.test_admin = auth_test_admin()
        self.test_user = auth_test_user()
        self.test_phases = get_test_phases()
        self.test_phases_nontimed = get_test_phases_nontimed()
        self.test_phases_timed = get_test_phases_timed()
    
    # Test methods
    ## Only allow admins to create courses
    def test_permission_course_creation(self):
        # Course creation by admin should get status code 201
        response = create_test_course_response(self.test_admin, 'Test Course Permission', self.test_phases, self.test_phases_nontimed, self.test_phases_timed)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Course creation by any other user should get a 403 error (as defined in exceptions.py of rest_framework)
        response = create_test_course_response(self.test_user, 'Test Course Permission', self.test_phases, self.test_phases_nontimed, self.test_phases_timed)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestApiParticipationCreation(APITestCase):
    # Test fixtures
    def setUp(self):
        self.test_admin = auth_test_admin()
        self.test_user = auth_test_user()
        self.test_phases = get_test_phases()
        self.test_phases_nontimed = get_test_phases_nontimed()
        self.test_phases_timed = get_test_phases_timed()
        self.test_participation_phase = 0

    ## Only allow users or admins to create course participations
    def test_permission_participation_creation(self):
        # Create test course as reference
        response_course_creation = create_test_course_response(self.test_admin, 'Test Course Participation', self.test_phases, self.test_phases_nontimed, self.test_phases_timed)
        # Participation creation by test user should get status code 201
        response = create_test_participation_response(self.test_user, response_course_creation.data['course_id'], 0)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    ## Only allow users or admins to view user-specific course participations
    def test_permission_participation_view(self):
        # Create test course as reference
        response_course_creation = create_test_course_response(self.test_admin, 'Test Course Participation', self.test_phases, self.test_phases_nontimed, self.test_phases_timed)
        # Create test participation
        response_participation_creation = create_test_participation_response(self.test_user, response_course_creation.data['course_id'], 4)
        # Get participation view response
        response = get_test_participation_response(self.test_user)
        # Participation view response by test user should only show one participation
        self.assertEqual(len(response.data), 1)
        # Participation view response by test user should only show participation of this user
        self.assertEqual(response.data[0]['user_id'], self.test_user.id)

class TestApiParticipationUpdate(APITestCase):
    # Test fixtures
    def setUp(self):
        self.test_admin = auth_test_admin()
        self.test_user = auth_test_user()
        self.test_phases = get_test_phases()
        self.test_phases_nontimed = get_test_phases_nontimed()
        self.test_phases_timed = get_test_phases_timed()
        self.test_course_1 = create_test_course_response(self.test_admin, 'Test Course 1 Participation Update', self.test_phases, self.test_phases_nontimed, self.test_phases_timed)
        self.test_course_2 = create_test_course_response(self.test_admin, 'Test Course 2 Participation Update', self.test_phases, self.test_phases_nontimed, self.test_phases_timed)
        self.test_participation_course_phase_initial_nontimed = eval(self.test_phases).index(eval(self.test_phases_nontimed)[0])
        self.test_participation_course_phase_initial_timed = eval(self.test_phases).index(eval(self.test_phases_timed)[0])
        self.test_participation = create_test_participation_response(
            self.test_user,
            self.test_course_1.data['course_id'],
            self.test_participation_course_phase_initial_nontimed
        )

    # Only allow jumps between course phases in participation updates, but not jumps in courses
    def test_participation_update(self):
        # Participation update by test user should succeed if updating course phase only
        response_a = create_test_participation_update_response(self.test_user, self.test_participation.data['participation_id'], self.test_course_1.data['course_id'], 1)
        self.assertEqual(response_a.status_code, status.HTTP_200_OK)
        # Participation update by test user should fail if updating course id
        response_b = create_test_participation_update_response(self.test_user, self.test_participation.data['participation_id'], self.test_course_2.data['course_id'], 0)
        self.assertEqual(response_b.status_code, status.HTTP_400_BAD_REQUEST)
        # Participation update by test user should fail if updating course id and course phase
        response_c = create_test_participation_update_response(self.test_user, self.test_participation.data['participation_id'], self.test_course_2.data['course_id'], 1)
        self.assertEqual(response_c.status_code, status.HTTP_400_BAD_REQUEST)

class TestApiParticipationCreationRuntimeUpdate(APITestCase):
    # Test fixtures
    def setUp(self):
        self.test_admin = auth_test_admin()
        self.test_user_1 = auth_test_user()
        self.test_user_2 = auth_test_user()
        self.test_user_3 = auth_test_user()
        self.test_phases = get_test_phases()
        self.test_phases_nontimed = get_test_phases_nontimed()
        self.test_phases_timed = get_test_phases_timed()
        self.test_course = create_test_course_response(self.test_admin, 'Test Course Participation', self.test_phases, self.test_phases_nontimed, self.test_phases_timed)
        self.test_participation_course_phase_initial_nontimed = eval(self.test_phases).index(eval(self.test_phases_nontimed)[0])
        self.test_participation_course_phase_initial_timed = eval(self.test_phases).index(eval(self.test_phases_timed)[0])

    # Test methods
    def test_participation_creation_runtime_update(self):
        # Participation creation with
        # ├─ first user entering a nontimed phase
        # should
        # ├─ not update course_starttime
        # └─ not update course_runtime
        self.test_participation_1_phase_nontimed = create_test_participation_response(
            self.test_user_1,
            self.test_course.data['course_id'],
            self.test_participation_course_phase_initial_nontimed
        )

        participation_1_id = self.test_participation_1_phase_nontimed.data['participation_id']
        participation_course_id = self.test_participation_1_phase_nontimed.data['participation_course_id']

        course_object_values_pre = Course.objects.filter(course_id=participation_course_id).values()[0]
        delay_user_1_entering = 1.0
        time.sleep(delay_user_1_entering)
        response = create_test_participation_update_response(self.test_user_1, participation_1_id, participation_course_id, self.test_participation_course_phase_initial_nontimed)
        course_object_values_post = Course.objects.filter(course_id=participation_course_id).values()[0]

        self.assertEqual(course_object_values_post['course_starttime'], course_object_values_pre['course_starttime'])
        self.assertEqual(course_object_values_post['course_runtime'], course_object_values_pre['course_runtime'])

        # Participation creation with
        # ├─ second user entering a timed phase
        # should
        # ├─ update course_starttime
        # └─ update course_runtime by specified delay_user_2_entering
        participation_course_id = self.test_course.data['course_id']

        delay_user_2_entering = 1.0
        time.sleep(delay_user_2_entering)
        response_course_list = get_test_course_response(self.test_admin)

        course_object_values_pre = Course.objects.filter(course_id=participation_course_id).values()[0]
        response = create_test_participation_response(self.test_user_2, participation_course_id, self.test_participation_course_phase_initial_timed)
        delay_user_2_post_entering = 1.0
        time.sleep(delay_user_2_post_entering)
        response_course_list = get_test_course_response(self.test_admin)

        course_object_values_post = Course.objects.filter(course_id=participation_course_id).values()[0]

        self.assertNotEqual(course_object_values_post['course_starttime'], course_object_values_pre['course_starttime'])
        self.assertEqual(course_object_values_post['course_runtime'], course_object_values_pre['course_runtime'] + delay_user_2_post_entering)

        # Participation creation with
        # ├─ third user entering a timed phase
        # should
        # ├─ not update course_starttime
        # └─ update course_runtime by specified delay_user_3_entering
        self.test_participation_3_phase_timed = create_test_participation_response(
            self.test_user_3,
            self.test_course.data['course_id'],
            self.test_participation_course_phase_initial_timed
        )

        participation_3_id = self.test_participation_3_phase_timed.data['participation_id']
        participation_course_id = self.test_participation_3_phase_timed.data['participation_course_id']

        course_object_values_pre = Course.objects.filter(course_id=participation_course_id).values()[0]
        delay_user_3_entering = 1.0
        time.sleep(delay_user_3_entering)
        response = create_test_participation_update_response(self.test_user_3, participation_3_id, participation_course_id, self.test_participation_course_phase_initial_timed)
        course_object_values_post = Course.objects.filter(course_id=participation_course_id).values()[0]

        self.assertEqual(course_object_values_post['course_starttime'], course_object_values_pre['course_starttime'])
        self.assertEqual(course_object_values_post['course_runtime'], course_object_values_pre['course_runtime'] + delay_user_3_entering)

class TestApiParticipationRuntimeUpdate(APITestCase):
    # Test fixtures
    def setUp(self):
        self.test_admin = auth_test_admin()
        self.test_user_1 = auth_test_user()
        self.test_user_2 = auth_test_user()
        self.test_phases = get_test_phases()
        self.test_phases_nontimed = get_test_phases_nontimed()
        self.test_phases_timed = get_test_phases_timed()
        self.test_course = create_test_course_response(self.test_admin, 'Test Course Participation', self.test_phases, self.test_phases_nontimed, self.test_phases_timed)
        self.test_participation_course_phase_initial_nontimed = eval(self.test_phases).index(eval(self.test_phases_nontimed)[0])
        self.test_participation_course_phase_initial_timed = eval(self.test_phases).index(eval(self.test_phases_timed)[0])
        self.test_participation = create_test_participation_response(
            self.test_user_1,
            self.test_course.data['course_id'],
            self.test_participation_course_phase_initial_nontimed
        )
        self.test_participation_2 = create_test_participation_response(
            self.test_user_2,
            self.test_course.data['course_id'],
            self.test_participation_course_phase_initial_nontimed
        )

    # Test methods
    def test_participation_update_first_users(self):
        participation_1_id = self.test_participation.data['participation_id']
        participation_2_id = self.test_participation_2.data['participation_id']
        participation_course_id = self.test_participation.data['participation_course_id']

        # Participation update with
        # ├─ first user entering a lobby phase
        # should
        # ├─ not update course_starttime
        # └─ update course_runtime to delay_user_1_entering
        course_object_values_pre = Course.objects.filter(course_id=participation_course_id).values()[0]
        delay_user_1_entering = 0.0
        time.sleep(delay_user_1_entering)
        response = create_test_participation_update_response(self.test_user_1, participation_1_id, participation_course_id, self.test_participation_course_phase_initial_nontimed)
        course_object_values_post = Course.objects.filter(course_id=participation_course_id).values()[0]

        self.assertEqual(course_object_values_post['course_starttime'], course_object_values_pre['course_starttime'])
        self.assertEqual(course_object_values_post['course_runtime'], delay_user_1_entering)

        # Participation update with
        # ├─ first user entering a nonlobby phase
        # should
        # ├─ update course_starttime
        # └─ set course_runtime to 0
        course_object_values_pre = Course.objects.filter(course_id=participation_course_id).values()[0]
        delay_user_1_entering = 1.0
        time.sleep(delay_user_1_entering)
        response = create_test_participation_update_response(self.test_user_1, participation_1_id, participation_course_id, self.test_participation_course_phase_initial_timed)
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
        response = create_test_participation_update_response(self.test_user_2, participation_2_id, participation_course_id, self.test_participation_course_phase_initial_timed)
        course_object_values_post_2 = Course.objects.filter(course_id=participation_course_id).values()[0]
        self.assertEqual(course_object_values_post_2['course_starttime'], course_object_values_post['course_starttime'])
        self.assertEqual(course_object_values_post_2['course_runtime'], delay_user_2_entering)

        # Participation update with
        # ├─ first user being in a nonlobby phase
        # ├─ second user being in a nonlobby phase
        # ├─ second user entering a lobby phase
        # should
        # ├─ not update course_starttime
        # └─ update course_runtime to specified delay_user_2_entering + delay_user_2_exiting
        delay_user_2_exiting = 1.0
        time.sleep(delay_user_2_exiting)
        response = create_test_participation_update_response(self.test_user_2, participation_2_id, participation_course_id, self.test_participation_course_phase_initial_nontimed)
        course_object_values_post_3 = Course.objects.filter(course_id=participation_course_id).values()[0]
        self.assertEqual(course_object_values_post_3['course_starttime'], course_object_values_post_2['course_starttime'])
        self.assertEqual(course_object_values_post_3['course_runtime'], delay_user_2_entering + delay_user_2_exiting)

        # Participation update with
        # ├─ first user being in a nonlobby phase
        # ├─ first user entering a lobby phase
        # ├─ no other user being in a nonlobby phase
        # should
        # ├─ not update course_starttime
        # └─ achieve that course_runtime stays at its former value (timer halted)
        delay_user_1_exiting = 1.0
        time.sleep(delay_user_1_exiting)
        response_course_list = get_test_course_response(self.test_admin)
        response = create_test_participation_update_response(self.test_user_1, participation_1_id, participation_course_id, self.test_participation_course_phase_initial_nontimed)
        delay_user_1_post_exiting = 1.0
        time.sleep(delay_user_1_post_exiting)
        response_course_list = get_test_course_response(self.test_admin)
        course_object_values_post_4 = Course.objects.filter(course_id=participation_course_id).values()[0]
        self.assertEqual(course_object_values_post_4['course_starttime'], course_object_values_post_3['course_starttime'])
        self.assertEqual(course_object_values_post_4['course_runtime'], course_object_values_post_3['course_runtime'] + delay_user_1_exiting)

if __name__ == '__main__':
    unittest.main()
