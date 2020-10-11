from django.urls import path
from api import views

from django.conf.urls import include

urlpatterns = [
    path('courses/', views.CourseList.as_view()),
]