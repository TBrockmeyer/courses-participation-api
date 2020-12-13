# courses-participation-api
Simple web API for managing course participations, according to these rough requirements:

## Functionalities
### For admins:
- allow course creation
- allow user management (user creation, kicking users from courses...)

### For users:
- allow entering and exiting courses
- allow visibility of participation in courses

# How to use it
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

## For admins
### Admin course management
Create Courses
<br/>`http -a admin:admin POST http://127.0.0.1:8000/courses/ course_title="Course 7" course_phases="['Lobby', 'Welcome', 'Warmup']"`

Get all courses
<br/>`http -a admin:admin GET http://127.0.0.1:8000/courses/`

Delete courses
<br/>`http -a admin:admin DELETE http://127.0.0.1:8000/courses/admindelete/7/`

Remove user from course
<br/>`http -a admin:admin DELETE http://127.0.0.1:8000/participations/admindelete/ user_id=4`

### Admin participation management
Create participation for user
<br/>`http -a admin:admin POST http://127.0.0.1:8000/participations/create/ participation_course_id=1 participation_course_phase=0 user_id=1`

Get all participations
<br/>`http -a admin:admin GET http://127.0.0.1:8000/participations/`

Delete participation
<br/>`http -a admin:admin DELETE http://127.0.0.1:8000/participations/admindelete/ user_id=1`

## For users
Enter course (create participation)
<br/>`http -a user_4:user4_pw POST http://127.0.0.1:8000/participations/create/ participation_course_id=8 participation_course_phase=1`

Get own current course participation
<br/>`http -a user_4:user4_pw GET http://127.0.0.1:8000/participations/`

Exit course (delete own participation)
<br/>`http -a user_4:user4_pw DELETE http://127.0.0.1:8000/participations/delete/`

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
