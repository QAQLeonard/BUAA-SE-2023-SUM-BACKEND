from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import prototype_views, doc_views, project_views, node_views

urlpatterns = [
    path('create_project', project_views.create_project),
    path('update_project', project_views.update_project),
    path('delete_project', project_views.delete_project),
    path('restore_project', project_views.restore_project),
    path('get_team_projects', project_views.get_team_projects),
    path('get_project', project_views.get_project),
    path('copy_project', project_views.copy_project),

    path('create_prototype', prototype_views.create_prototype),
    path('update_prototype', prototype_views.update_prototype),
    path('delete_prototype', prototype_views.delete_prototype),
    path('restore_prototype', prototype_views.restore_prototype),
    # path('get_prototype_file', prototype_views.get_prototype_file),
    path('get_project_prototypes', prototype_views.get_project_prototypes),
    path('get_prototype', prototype_views.get_prototype),
    path('save_prototype_preview', prototype_views.save_prototype_preview),
    path('get_project_prototype_previews', prototype_views.get_project_prototype_previews),

    path('create_doc', doc_views.create_doc),
    path('delete_doc', doc_views.delete_doc),
    path('update_doc', doc_views.update_doc),
    path('get_doc_permissions', doc_views.get_doc_permissions),
    path('get_project_docs', doc_views.get_project_docs),
    path('get_doc_team_id', doc_views.get_doc_team_id),
    path('get_doc', doc_views.get_doc),
    path('convert_format', doc_views.convert_format),
    path('docs/<str:doc_id>/data/', doc_views.DocumentData.as_view(), name='document_data'),

    path('get_node', node_views.get_node),
    path('get_all_nodes', node_views.get_all_nodes),
    path('get_children_nodes', node_views.get_children_nodes),
    path('add_node', node_views.add_node),
    path('update_node', node_views.update_node),
    path('delete_node', node_views.delete_node),
]
