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

# How to use it (if using the UI via https://course-participation-api.herokuapp.com/home/)

## Login as admin
Go to http://127.0.0.1:8000/api-auth/login/?next=/courses/ and login as admin.
- username: [provided in personal message]
- password: [provided in personal message]

## Create courses
Go to http://127.0.0.1:8000/courses/create/ and create courses with course title and the timed and non-timed phases of the course ('non-timed' meaning: the timer is halted if all course participants are only in a non-timed phase). Please find an example how to define the course phases below. Open the URL, enter the example details and click the 'POST' button to create the new course. You can leave the course_runtime fields empty or fill them; please note that they will only be updated as soon as users start participating in the course (handled further below).

Example:
- Course title: Course 5
- Course phases: ['Lobby Start', 'Welcome', 'Push', 'Lobby End']
- Course phases timed: ['Welcome', 'Push']
- Course phases nontimed: ['Lobby Start', 'Lobby End']

## List / view all courses
Go to http://127.0.0.1:8000/courses/ and view a list of all courses.

## Delete courses
Go to http://127.0.0.1:8000/courses/admindelete/2/ and delete the course you just created (or any other course you don't want to keep). Determine the course_id of your course with the course list endpoint introduced above, and replace the "1" in the URL with it. After opening the URL, click the 'DELETE' button to actually delete the course.

## View all users
Go to http://127.0.0.1:8000/users/ and view a list of all users.

## Create new users
Go to http://127.0.0.1:8000/users/ and create new users. For this demo, the password will be the same as the username you're entering. Open the URL, enter the example details and click the 'POST' button to create the new user. Users user_2 to user_5 have already been pre-created.

Example:
- Username: user_6
- (Password [will be set automatically]: user_6)

## Log out, and login as user
Log out, go to http://127.0.0.1:8000/api-auth/login/?next=/courses/ and login again as a normal user.
Login with e.g. the following credentials:
- username: user_2
- password: user_2
Or
- username: user_3
- password: user_3
or any other user ... users user_2 to user_5 have been pre-created.

## View all courses
Go to http://127.0.0.1:8000/courses/ and view all courses and the available phases. For the step below, remember already now the course_id (e.g. '3') of the course you'd like to participate in, and the index of a timed phase in the list of all phases of the course; e.g. remember '2' if the timed phases are ['Welcome', 'Push'] and all phases are ['Lobby Start', 'Welcome', 'Push', 'Lobby End']. Why is '2' a valid index of a timed phase? Because 'Push' is in position 2 among the indices of all course phases (0: 'Lobby Start', 1: 'Welcome', 2: 'Push', 3: 'Lobby End'), and phase 2: 'Push' is a timed phase.

## Create a course participation
Go to http://127.0.0.1:8000/participations/create/ and create a course participation for the logged-in user. Provide the course_id of the course you want to enter (e.g., '3'), and provide the index of a timed participation (e.g. '2') so that course timers start. Open the URL, enter the example details and click the 'POST' button to create the new participation.

Example:
- Participation course id: Course object (3) [this is the course with the course ID 3]
- Participation course phase: 2 [or the index of any timed phase you remembered from the course]

## Wait a few seconds. View all courses
Wait a few seconds. Then go to http://127.0.0.1:8000/courses/ and view all courses. Note that the course_runtime and course_runtime_formatted for the course you're participating in now also show some seconds passed. Reload page to verify (course_runtime_formatted always updated to its current number of seconds).

## View your existing participation
Go to http://127.0.0.1:8000/participations and view your existing participation. Empty if no participation created yet. Remember your participation_id if available.

## Update your participation
Go to http://127.0.0.1:8000/participations/update/1 to update your participation (replace 1 by your participation_id if necessary). For participation_course_phase, enter the index of a non-timed phase (e.g. "0").

Example:
- Participation course phase: 0

## Wait a few seconds. View all courses
Go to http://127.0.0.1:8000/courses/ and view all courses. Note that the course_runtime and course_runtime_formatted for the course you're participating in now show a paused timer. Reload page to verify (course_runtime_formatted persists at its paused number of seconds runtime).

## Delete your participation
Go to http://127.0.0.1:8000/participations/delete/ to delete your participation in the course. Open the URL, and click on the red button 'DELETE' to delete it. View your participations again to verify that it has been deleted.

## Create a course participation again
Go to http://127.0.0.1:8000/participations/create/ and create a participation again, as before.

## Log out, and login as admin
As before:
- username: [provided in personal message]
- password: [provided in personal message]

## View all existing participations
Go to http://127.0.0.1:8000/participations and view all existing participations. If you want to kick a user from the course, remember the participation_id of the user you want to kick

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
