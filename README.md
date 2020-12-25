# courses-participation-api
Simple web API for managing course participations, according to these rough requirements:

## Functionalities
### For admins:
- allow course creation
- allow user management (user creation, kicking users from courses...)

### For users:
- allow entering and exiting courses
- allow visibility of participation in courses

### ---------------------------------------

# How to use it (if using the UI via TODO: provide URL)

## Login as admin
- username: [provided in personal message]
- password: [provided in personal message]

## Create courses
Go to http://127.0.0.1:8000/courses/create/ and create courses

## Delete courses
Go to http://127.0.0.1:8000/courses/admindelete/1/ and delete the first course you created (or any other course you don't want to keep)

## View all courses
Go to http://127.0.0.1:8000/courses/ and view all courses

## View all users
Go to http://127.0.0.1:8000/users/ and view all users

## Log out, and login as user
Login with e.g. the following redentials:
- username: user_2
- password: user2_pw
Or
- username: user_3
- password: user3_pw
or any other user ... users user_2 to user_5 are pre-created

## View all courses
Go to http://127.0.0.1:8000/courses/ and view all courses and the available phases. Remember the index of a timed phase of one course in the list of all phases; e.g. remember "2" if the timed phases are "['Welcome', 'Push']" and all phases are "['Lobby Start', 'Welcome', 'Push', 'Lobby End']" ("Push" in position 2 among 0,1,2,3)

## Create a course participation
Go to http://127.0.0.1:8000/participations/create/ and create a participation. Provide the index of the course phase you want to enter. Provide the index of a timed participation (e.g. "2") if course timers shall start.

## View your existing participation
Go to http://127.0.0.1:8000/participations and view your existing participation. Empty if none. Remember your participation_id if available.

## Update your participation
Go to http://127.0.0.1:8000/participations/update/1 to update your participation (replace 1 by your participation_id if necessary)

## Delete your participation
Go to http://127.0.0.1:8000/participations/delete/ to delete your participation in the course. Click on the red button "DELETE" to delete it.

## Create a course participation again
Go to http://127.0.0.1:8000/participations/create/ and create a participation again, as before.

## Wait a few seconds. View all courses
Go to http://127.0.0.1:8000/courses/ and view all courses. Note that the course_runtime and course_runtime_formatted now also show some seconds passed.

## Log out, and login as admin
As before:
- username: [provided in personal message]
- password: [provided in personal message]

## View all existing participations
Go to http://127.0.0.1:8000/participations and view all existing participations. Remember the participation_id of the user you want to kick

## Kick a user from the course
Go to http://127.0.0.1:8000/participations/admindelete/2 to delete participation 2 (or replace "2" with any other participation_id)

## Repeat to see course_runtime field changes
Repeat the steps from logging in as a user, creating a participation, updating between timed and nontimed phases to see the effects on the course_runtime fields. Timer will stop if no users are in timed phases anymore, and reset itself if users enter timed phases again.

### ---------------------------------------

# How to use it (if cloning the repository to local and executing commands via command line)
## Set up your environment
- clone the repo
- cd into the folder "courseparticipation"
- install required packages
<br/>`pip install django`
<br/>`pip install djangorestframework`
- in a first terminal, cd into the parent folder of "courseparticipation" and do
<br/>`python manage.py runserver`
- in a second terminal, try out the commands below to interact with the API
- if any requirement is missing, check out this link and follow the first steps until you have a running minimalistic API. Then use a similar configuration to run this API.
<br/>https://www.django-rest-framework.org/tutorial/1-serialization/

## Create users, courses and participations for testing the API
### Create admin user
```
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user=User.objects.create_user('admin', password='admin')
>>> user.is_superuser=True
>>> user.is_staff=True
>>> user.save()
>>> exit()
```
### Create standard users
```
python manage.py shell
>>> user=User.objects.create_user('user_2', password='user2_pw')
>>> user.is_superuser=False
>>> user.is_staff=False
>>> user.save()
>>> user=User.objects.create_user('user_3', password='user3_pw')
>>> user.is_superuser=False
>>> user.is_staff=False
>>> user.save()
>>> user=User.objects.create_user('user_4', password='user4_pw')
>>> user.is_superuser=False
>>> user.is_staff=False
>>> user.save()
>>> exit()
```

### Test the API by creating courses (as admin) and managing participations (as admin, and as user)
## For admins
### Admin course management
Create Courses
<br/>`http -a admin:admin POST http://127.0.0.1:8000/courses/ course_title="Course 1" course_phases="['Lobby', 'Welcome', 'Warmup']"`

Get all courses
<br/>`http -a admin:admin GET http://127.0.0.1:8000/courses/`

Delete courses
<br/>`http -a admin:admin DELETE http://127.0.0.1:8000/courses/admindelete/1/`
<br/>The primary key int:pk, here "1", is the course_id; it can be determined by getting all courses and their course_id, see paragraph above

Remove user from course
<br/>`http -a admin:admin DELETE http://127.0.0.1:8000/participations/admindelete/ user_id=1`

### Admin participation management
Create participation for user
<br/>`http -a admin:admin POST http://127.0.0.1:8000/participations/create/ participation_course_id=1 participation_course_phase=0 user_id=1`

Get all participations
<br/>`http -a admin:admin GET http://127.0.0.1:8000/participations/`

Update course phase of a user's current course participation
<br/>`http -a admin:admin PUT http://127.0.0.1:8000/participations/update/1/ participation_course_id=1 participation_course_phase=1`
<br/>`http -a admin:admin PUT http://127.0.0.1:8000/participations/update/1/ participation_course_id=1 participation_course_phase=2`
<br/>The primary key int:pk, here "1", is the participation_id; it can be determined by getting the user's currently valid course participation, see paragraph above

Delete participation (kick user from course)
<br/>`http -a admin:admin DELETE http://127.0.0.1:8000/participations/admindelete/ user_id=1`

## For users
Enter course (create participation)
<br/>`http -a user_2:user2_pw POST http://127.0.0.1:8000/participations/create/ participation_course_id=2 participation_course_phase=0`

Get participation_course_phase and participation_id of own current course participation
<br/>`http -a user_2:user2_pw GET http://127.0.0.1:8000/participations/`

Update own current course participation
<br/>`http -a user_2:user2_pw PUT http://127.0.0.1:8000/participations/update/2/ participation_course_id=2 participation_course_phase=1`
<br/>The primary key int:pk, here "2", is the participation_id; it can be determined by getting the currently valid course participation, see paragraph above

Exit course (delete own participation)
<br/>`http -a user_2:user2_pw DELETE http://127.0.0.1:8000/participations/delete/`

# How to create it
## How to learn to create web APIs with Django
Follow the web API tutorial on the Website of the Django Rest Framework.<br/>Start with Step 1 here: https://www.django-rest-framework.org/tutorial/1-serialization/

Pay special attention to how
- models and serializers
- views and urls
- permissions
go hand in hand to manage requests to the API.

## Set up the build with Travis CI
Go to travis-ci.com and follow instructions for how to integrate e.g. your GitHub project.

For an intro on how to create automated tests, read the article on the unittest package on https://docs.python.org/3/library/unittest.html

For how to set up automated testing of every build in Travis CI, read this article on how to build a Python project with Travis CI: https://docs.travis-ci.com/user/languages/python/
