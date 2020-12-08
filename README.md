# courses-participation-api
Simple web API for managing course participations, according to these rough requirements:

## For admins:
- allow course creation
- allow user management (user creation, kicking users from courses...)

## For users:
- allow entering and exiting courses
- allow visibility of participation in courses

# How to learn how to create web APIs
Follow the web API tutorial on the Website of the Django Rest Framework.<br/>Start with Step 1 here: https://www.django-rest-framework.org/tutorial/1-serialization/

# How to use it
## Set up your environment
- clone the repo
- cd into the folder "courseparticipation"
- install required packages
<br/>`pip install django`
pip install djangorestframework`
- in a first terminal, cd into the parent folder of "courseparticipation" and do
<br/>`python manage.py runserver`
- in a second terminal, try out the commands below to interact with the API
- if any requirement is missing, check out this link and follow the first steps until you have a running minimalistic API. Then use a similar configuration to run this API.
<br/>https://www.django-rest-framework.org/tutorial/1-serialization/

## For admins
Create Courses
<br/>`http -a admin:admin POST http://127.0.0.1:8000/courses/ course_title="Course 7" course_phases="['Lobby', 'Welcome', 'Warmup']"`

Get all courses
<br/>`http -a admin:admin GET http://127.0.0.1:8000/courses/`

Delete courses
<br/>`http -a admin:admin DELETE http://127.0.0.1:8000/courses/admindelete/7/`

Remove user from course
<br/>`http -a admin:admin DELETE http://127.0.0.1:8000/participations/admindelete/ user_id=4`

## For users
Enter course
<br/>`http -a user_4:user4_pw POST http://127.0.0.1:8000/participations/create/ participation_course_id=8 participation_course_phase=1`

Get own current course participation
<br/>`http -a user_4:user4_pw GET http://127.0.0.1:8000/participations/`

Exit course
<br/>`http -a user_4:user4_pw DELETE http://127.0.0.1:8000/participations/delete/`

## Set up the build with Travis CI
Go to travis-ci.com and follow instructions for how to integrate e.g. your GitHub project
