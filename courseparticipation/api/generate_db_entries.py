from django.core.wsgi import get_wsgi_application
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courseparticipation.settings')

application = get_wsgi_application()

from django.conf import settings
if not settings.configured:
    settings.configure()

from django.contrib.auth.models import User

class DbEntriesCreation:
    def create_user(self, username, password, is_superuser, is_staff):
        self.user=User.objects.create_user(username, password=password)
        self.user.is_superuser=is_superuser
        self.user.is_staff=is_staff
        self.user.save()

    def create_user_admin(self):
        self.user_creation = self.create_user('admin', 'admin', True, True)

    def create_user_examples(self, number_examples):
        self.user_examples_usernames = ["user_"+str(i) for i in range (0,number_examples)]
        self.user_examples_passwords = ["user"+str(i)+"_pw" for i in range (0,number_examples)]
        for j in range (0, number_examples):
            try:
                self.create_user(self.user_examples_usernames[j], self.user_examples_passwords[j], False, False)
            except:
                pass
