from django.core.wsgi import get_wsgi_application
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courseparticipation.settings')

application = get_wsgi_application()

from django.conf import settings
if not settings.configured:
    settings.configure()

from django.contrib.auth.models import User
from api.models import Course, Participation

from django.utils import timezone, dateformat

import datetime

"""
Method to re-calculate passed days, hours, minutes, seconds from given seconds
Adapted from: https://stackoverflow.com/questions/4048651/python-function-to-convert-seconds-into-minutes-hours-and-days
"""

def display_time(seconds, granularity=2):
    intervals = (
        ('days', 86400),    # 60 * 60 * 24
        ('hours', 3600),    # 60 * 60
        ('minutes', 60),
        ('seconds', 1),
    )

    result = []

    granularity = 3 if seconds >= 3600 else granularity
    granularity = 4 if seconds >= 86400 else granularity

    for _, count in intervals:
        value = seconds // count
        seconds -= value * count
        result.append("{}".format(value).zfill(2))
    return ':'.join(result[-granularity:])

class DbEntriesUpdate:
    def __init__(self):
        self.tmp = 0

    def update_course_time(self, course_id_list, reset_runtime):
        """
        Update the fields course_starttime, course_runtime, course_runtime_formatted.
        This method needs to be called each time after one of the following views is returned:
        ├─ CourseList (url: courses/) (all courses are listed) (r if request.data['participation_course_phase'] in nonlobby phases)
        ├─ ParticipationCreation (url: participations/create/) (user enters course)
        ├─ ParticipationDeletion (url: participations/delete/) (user leaves course)
        ├─ ParticipationDeletionByAdmin (url: participations/admindelete/) (user is kicked from course by admin)
        └─ ParticipationUpdate (url: participations/update/) (a user transitions between course phases) (r)
        (r: reset_runtime = True)

        """

        # TODO: [UCT - tests] Write test cases for all possible combinations of users distributed over the course phases (lobby / non-lobby / no users at all)
        # and for each combination, all possible transitions (from lobby to non-lobby, directly into lobby, directly into non-lobby, directly from non-lobby out (harsh exit / kicked))
        # TODO: [UCT - cleanup] delete old course runtime update VIEW?
        # TODO: [UCT - imple] call class CourseUpdateRuntime whenever a transition is happening or courses view requested
        # TODO: [UCT - imple] write an endpoint to retrieve the course_runtime_formatted
        # TODO: [UCT - permissions] change the permissions for this class to "IsAdminUser", and ensure that those methods calling it internally set the request.user.is_staff to True
        # TODO: [UCT - refac] refine the configurability of the phases: timed or not timed? --> number_users_lobby and number_users_nonlobby will depend on that
        # └─ rename _lobby and _nonlobby to _nontimed and _timed

        relevant_course_id = course_id_list[0]
        existing_course_values = list(Course.objects.filter(course_id=relevant_course_id).values())[0]
        existing_course_starttime = existing_course_values['course_starttime']

        existing_course_phase_max = len(eval(existing_course_values['course_phases'])) - 1

        number_users_lobby_start = int(len(list(Participation.objects.filter(participation_course_id=relevant_course_id, participation_course_phase=0).values())))
        number_users_lobby_end = int(len(list(Participation.objects.filter(participation_course_id=relevant_course_id, participation_course_phase=existing_course_phase_max).values())))
        number_users_course = int(len(list(Participation.objects.filter(participation_course_id=relevant_course_id).values())))
        number_users_lobby = number_users_lobby_start + number_users_lobby_end
        number_users_nonlobby = number_users_course - number_users_lobby
        number_users_phase_first_timed = int(len(list(Participation.objects.filter(participation_course_id=relevant_course_id, participation_course_phase=1).values())))

        date_format_datetime = '%Y-%m-%d %H:%M:%S'
        date_format_timezone = 'Y-m-d H:i:s'

        if(number_users_phase_first_timed == 1 and number_users_nonlobby == 1 and reset_runtime):
            # "There is exactly one user inside the first timed phase of the course, and the requested course_runtime is 0"
            # Whenever a user switches from phase 0 ('Lobby Start') to phase 1 ('Warmup'),
            # the update call tries to indicate that this is a "runtime reset" call,
            # i.e. that it's the first user entering and thus starting the course.
            # We follow this indication only if there are no other users anywhere in the course,
            # except for the first lobby phase ('Lobby Start').
            # Set course_starttime to now.
            # Set course-runtime to 0.
            course_starttime = timezone.now()
            course_runtime = 0
            course_runtime_formatted = display_time(course_runtime)
            Course.objects.filter(course_id=relevant_course_id).update(course_starttime=course_starttime, course_runtime=course_runtime, course_runtime_formatted=course_runtime_formatted)
        

        elif(number_users_nonlobby == 0):
            # "There are no users in the non-lobby phases of the course"
            # This describes e.g. the cases where
            # ├─ a list of the courses is requested, and no user is inside the course
            # └─ the last user just left the course
            # Set course_starttime to 0000-00-00T00:00:00Z
            # Set course_runtime to 0
            course_starttime = existing_course_starttime
            course_runtime = 0
            course_runtime_formatted = display_time(course_runtime)
            Course.objects.filter(course_id=relevant_course_id).update(course_starttime=course_starttime, course_runtime=course_runtime, course_runtime_formatted=course_runtime_formatted)

        else:
            # "There are already/still users in the non-lobby phases of the course, and no reset_runtime is requested"
            # Set course_starttime to existing course_starttime
            # Set (update) course_runtime to timediff between now and course_starttime
            current_time = datetime.datetime.strptime(dateformat.format(timezone.now(), date_format_timezone), date_format_datetime)
            course_starttime = datetime.datetime.strptime(datetime.datetime.strftime(existing_course_starttime, date_format_datetime), date_format_datetime)
            timediff = int((current_time - course_starttime).total_seconds())
            course_starttime = existing_course_starttime
            course_runtime = timediff
            course_runtime_formatted = display_time(course_runtime)
            Course.objects.filter(course_id=relevant_course_id).update(course_starttime=course_starttime, course_runtime=course_runtime, course_runtime_formatted=course_runtime_formatted)


