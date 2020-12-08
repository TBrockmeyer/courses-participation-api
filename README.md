# courses-participation-api

# How to create it
Follow the web API tutorial on the Website of the Django Rest Framework.<br/>Start with Step 1 here: https://www.django-rest-framework.org/tutorial/1-serialization/

# How to use it
## For admins
Create Courses
`http -a admin:admin POST http://127.0.0.1:8000/courses/ course_title="Course 7" course_phases="['Lobby', 'Welcome', 'Warmup']"`

Get all courses
`http -a admin:admin GET http://127.0.0.1:8000/courses/`

Delete courses
`http -a admin:admin DELETE http://127.0.0.1:8000/courses/admindelete/7/`

Remove user from course
`http -a admin:admin DELETE http://127.0.0.1:8000/participations/admindelete/ user_id=4`

## For users
Enter course
`http -a user_4:user4_pw POST http://127.0.0.1:8000/participations/create/ participation_course_id=8 participation_course_phase=1`

Get own current course participation
`http -a user_4:user4_pw GET http://127.0.0.1:8000/participations/`

Exit course
`http -a user_4:user4_pw DELETE http://127.0.0.1:8000/participations/delete/`

## Set up the build with Travis CI
Go to travis-ci.com and follow instructions for how to integrate e.g. your GitHub project
