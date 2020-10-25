from django.core.wsgi import get_wsgi_application
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courseparticipation.settings')

application = get_wsgi_application()

from django.conf import settings
if not settings.configured:
    settings.configure()

from django.contrib.auth.models import User

class DbEntriesCreation:
    def __init__(self):
        self.test_admin_username = 'test_admin'
        self.test_admin_password = 'test_admin_pw'

    def create_user(self, username, password, is_superuser, is_staff):
        self.user=User.objects.create_user(username, password=password)
        self.user.is_superuser=is_superuser
        self.user.is_staff=is_staff
        self.user.save()

    def create_user_admin(self, username=None, password=None):
        username = self.test_admin_username if username==None else username
        password = self.test_admin_password if password==None else password
        try:
            self.create_user(username, password, True, True)
        except:
            print("User " + username + " already exists.")

    def create_user_examples(self, number_examples):
        self.user_examples_usernames = ["test_user_"+str(i) for i in range (0,number_examples)]
        self.user_examples_passwords = ["test_user"+str(i)+"_pw" for i in range (0,number_examples)]
        for j in range (0, number_examples):
            try:
                self.create_user(self.user_examples_usernames[j], self.user_examples_passwords[j], False, False)
            except:
                print("User " + self.user_examples_usernames[j] + " already exists.")

