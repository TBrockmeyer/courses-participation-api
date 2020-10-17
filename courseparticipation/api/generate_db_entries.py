from django.core.wsgi import get_wsgi_application
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courseparticipation.settings')

application = get_wsgi_application()

from django.conf import settings
if not settings.configured:
    settings.configure()

from django.contrib.auth.models import User

class DbEntriesCreation():
    def __init__(self):
        self.tmp = 0
    # self only needed if self.objects passed:
    # https://stackoverflow.com/questions/12179271/meaning-of-classmethod-and-staticmethod-for-beginner
    def create_user(username, password, is_superuser, is_staff):
        user=User.objects.create_user(username, password=password)
        user.is_superuser=True
        user.is_staff=True
        user.save()

    def create_user_admin():
        user_creation = self.create_user('admin', 'admin', True, True)

    def create_user_examples(number_examples):
        user_examples_usernames = ["user_"+str(i) for i in range (0,number_examples)]
        user_examples_passwords = ["user"+str(i)+"_pw" for i in range (0,number_examples)]
        for j in range (0, number_examples):
            try:
                self.create_user(user_examples_usernames[j], user_examples_passwords[j], False, False)
            except:
                pass
