from django.urls import path, include
from api import views

from django.conf.urls import include

urlpatterns = [
    path('courses/', views.CourseList.as_view()),
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('participations/', views.ParticipationList.as_view()),
    path('participations/create/', views.ParticipationCreation.as_view()),
    path('participations/update/<int:pk>/', views.ParticipationUpdate.as_view()),
    path('participations/delete/', views.ParticipationDeletion.as_view()),
    path('participations/admindelete/', views.ParticipationDeletionByAdmin.as_view()),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]