from django.urls import path, include
from api import views

from django.conf.urls import include

urlpatterns = [
    path('courses/', views.CourseList.as_view()),
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('participations/', views.ParticipationList.as_view()),
    path('participations/update/', views.ParticipationCreation.as_view()),
    path('participations/delete/<int:pk>/', views.ParticipationDeletion.as_view()),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]