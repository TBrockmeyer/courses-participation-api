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
        factory = APIRequestFactory()
        request = factory.get('/users/')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['username'], 'admin')

    def test_user_creation_10_users_list(self):
        view = UserList.as_view()
        number_users = 10
        DbEntriesCreation().create_user_examples(number_users)
        factory = APIRequestFactory()
        request = factory.get('/users/')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range (0, number_users):
            self.assertEqual(response.data[i]['username'], 'user_'+str(i))

if __name__ == '__main__':
    unittest.main()
