release: sh -c 'cd ./courseparticipation/ && python manage.py migrate'
web: gunicorn --chdir ./courseparticipation courseparticipation.wsgi --log-file -
