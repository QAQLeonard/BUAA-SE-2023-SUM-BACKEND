from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .views import prototype_views, doc_views

urlpatterns = [
    path('create_project', project_views.create_project),
    path('update_project', project_views.update_project),
    path('delete_project', project_views.delete_project),
    path('get_team_projects', project_views.get_team_projects),
    path('get_project', project_views.get_project),

    path('create_prototype', prototype_views.create_prototype),
    path('update_prototype', prototype_views.update_prototype),
    path('delete_prototype', prototype_views.delete_prototype),
    path('get_prototype_file', prototype_views.get_prototype_file),
    path('get_project_prototypes', prototype_views.get_prototypes),
    path('get_prototype', prototype_views.get_prototype),

    path('create_doc', doc_views.create_doc),
    path('delete_doc', doc_views.delete_doc),
    path('update_doc_permissions', doc_views.update_doc_permissions),
    path('get_doc_permissions', doc_views.get_doc_permissions),
    path('get_project_docs', doc_views.get_project_docs),
]
