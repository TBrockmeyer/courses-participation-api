import unittest

from api.views import CourseList
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

    def test_course_list(self):
        view = CourseList.as_view()
        #DbEntriesCreation().create_user_admin()
        #DbEntriesCreation().create_user_examples(10)
        #user_entries = User.objects.all()
        #print(user_entries.order_by("-date_joined").values())
        factory = APIRequestFactory()
        request = factory.get('/courses/')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

if __name__ == '__main__':
    unittest.main()
