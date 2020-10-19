import unittest

from api.views import CourseList, UserList
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
from rest_framework.test import APIRequestFactory, APITestCase

class TestApi(APITestCase):

    # Test scope: displaying courses list
    def test_course_list(self):
        view = CourseList.as_view()
        factory = APIRequestFactory()
        request = factory.get('/courses/')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test scope: creating users
    def test_user_creation_admin(self):
        view = UserList.as_view()
        DbEntriesCreation().create_user_admin()

        user_objects_list = list(User.objects.filter(username__startswith="test_admin").all().values())

        factory = APIRequestFactory()
        request = factory.get('/users/')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_objects_list[0]["username"], 'test_admin')

    def test_user_creation_10_users_list(self):
        view = UserList.as_view()
        number_users = 10
        DbEntriesCreation().create_user_examples(number_users)

        user_objects_list = list(User.objects.filter(username__startswith="user_").all().values())

        factory = APIRequestFactory()
        request = factory.get('/users/')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range (0, number_users):
            self.assertEqual(user_objects_list[i]['username'], 'user_'+str(i))

    # Test scope: user permissions
    ## Only allow admins to create courses
    #def test_permission_course_creation(self):


if __name__ == '__main__':
    unittest.main()
