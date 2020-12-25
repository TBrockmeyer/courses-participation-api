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
        ├─ CourseList (url: courses/) (all courses are listed) (r if request.data['participation_course_phase'] in timed phases)
        ├─ ParticipationCreation (url: participations/create/) (user enters course)
        ├─ ParticipationDeletion (url: participations/delete/) (user leaves course)
        ├─ ParticipationDeletionByAdmin (url: participations/admindelete/) (user is kicked from course by admin)
        └─ ParticipationUpdate (url: participations/update/) (a user transitions between course phases) (r)
        (r: reset_runtime = True)

        """

        if(len(course_id_list) > 0):
            pass
        else:
            return None

        for i in range(0, len(course_id_list)):
            relevant_course_id = course_id_list[i]

            relevant_course = Course.objects.filter(course_id=relevant_course_id)
            relevant_course_starttime = relevant_course.values()[0]['course_starttime']
            relevant_course_runtime = relevant_course.values()[0]['course_runtime']
            relevant_course_phases = eval(relevant_course.values()[0]['course_phases'])
            relevant_course_phases_timed = eval(relevant_course.values()[0]['course_phases_timed'])
            relevant_course_phases_nontimed = eval(relevant_course.values()[0]['course_phases_nontimed'])

            number_users_nontimed = 0

            for phase in relevant_course_phases_nontimed:
                phase_index = relevant_course_phases.index(phase)
                number_users_nontimed += int(len(list(Participation.objects.filter(participation_course_id=relevant_course_id, participation_course_phase=phase_index).values())))

            number_users_course = int(len(list(Participation.objects.filter(participation_course_id=relevant_course_id).values())))
            number_users_timed = number_users_course - number_users_nontimed

            phase_index_first_timed = relevant_course_phases.index(relevant_course_phases_timed[0]) if len(relevant_course_phases_timed) > 0 else 0
            number_users_phase_first_timed = int(len(list(Participation.objects.filter(participation_course_id=relevant_course_id, participation_course_phase=phase_index_first_timed).values()))) if len(relevant_course_phases_timed) > 0 else 0

            date_format_datetime = '%Y-%m-%d %H:%M:%S'
            date_format_timezone = 'Y-m-d H:i:s'

            if(number_users_phase_first_timed == 1 and number_users_timed == 1 and reset_runtime):
                # "There is exactly one user inside the first timed phase of the course, and the requested course_runtime is 0"
                # Whenever a user switches from phase 0 ('Lobby Start') to phase 1 ('Warmup'),
                # the update call tries to indicate that this is a "runtime reset" call,
                # i.e. that it's the first user entering and thus starting the course.
                # We follow this indication only if there are no other users anywhere in the course,
                # except for the firstnontimed phase ('Lobby Start').
                # Set course_starttime to now.
                # Set course-runtime to 0.
                course_starttime = timezone.now()
                course_runtime = 0
                course_runtime_formatted = display_time(course_runtime)
                Course.objects.filter(course_id=relevant_course_id).update(course_starttime=course_starttime, course_runtime=course_runtime, course_runtime_formatted=course_runtime_formatted)
            

            elif(number_users_timed == 0):
                # "There are no users in the timed phases of the course"
                # This describes e.g. the cases where
                # ├─ a list of the courses is requested, and no user is inside the course
                # └─ the last user just left the course
                # Set course_starttime to 0000-00-00T00:00:00Z
                # Set course_runtime to 0
                course_starttime = relevant_course_starttime
                course_runtime = relevant_course_runtime
                course_runtime_formatted = display_time(course_runtime)
                Course.objects.filter(course_id=relevant_course_id).update(course_starttime=course_starttime, course_runtime=course_runtime, course_runtime_formatted=course_runtime_formatted)

            else:
                # "There are already/still users in the timed phases of the course, and no reset_runtime is requested"
                # Set course_starttime to existing course_starttime
                # Set (update) course_runtime to timediff between now and course_starttime
                current_time = datetime.datetime.strptime(dateformat.format(timezone.now(), date_format_timezone), date_format_datetime)
                course_starttime = datetime.datetime.strptime(datetime.datetime.strftime(relevant_course_starttime, date_format_datetime), date_format_datetime)
                timediff = int((current_time - course_starttime).total_seconds())
                course_starttime = relevant_course_starttime
                course_runtime = timediff
                course_runtime_formatted = display_time(course_runtime)
                Course.objects.filter(course_id=relevant_course_id).update(course_starttime=course_starttime, course_runtime=course_runtime, course_runtime_formatted=course_runtime_formatted)


