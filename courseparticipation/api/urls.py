from django.urls import path
from api import views

from django.conf.urls import include

urlpatterns = [
    path('courses/', views.CourseList.as_view()),
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
]