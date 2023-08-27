from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
urlpatterns = [
    path('create_project', project_views.create_project),
    path('update_project', project_views.update_project),
    path('delete_project', project_views.delete_project),
    path('get_project', project_views.get_team_projects),
]
