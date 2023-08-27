from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .views import prototype_views

urlpatterns = [
    path('create_project', project_views.create_project),
    path('update_project', project_views.update_project),
    path('delete_project', project_views.delete_project),
    path('get_project', project_views.get_team_projects),

    path('create_prototype', prototype_views.create_prototype),
    path('update_prototype', prototype_views.update_prototype),
    path('delete_prototype', prototype_views.delete_prototype),
    path('get_prototype_file', prototype_views.get_prototype_file),
    path('get_project_prototypes', prototype_views.get_prototypes),
    path('get_prototype', prototype_views.get_prototype),
]
