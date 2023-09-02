from django.http import JsonResponse
from rest_framework import status

from TeamManagement.models import *
from ProjectExecution.models import *


def require_project(view_func):
    def _wrapped_view(request, *args, **kwargs):
        project_id = request.GET.get('project_id')
        if not project_id:
            project_id = request.data.get('project_id')

        if not project_id:
            return JsonResponse({'status': 'error', 'message': 'Missing project_id parameter'}, status=400)

        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Project does not exist'}, status=404)

        request.project_object = project  # Attach project to request object so that it's available in the view
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def require_doc(view_func):
    def _wrapped_view(request, *args, **kwargs):
        doc_id = request.GET.get('doc_id')
        if not doc_id:
            doc_id = request.data.get('doc_id')

        if not doc_id:
            return JsonResponse({'status': 'error', 'message': 'Missing doc_id parameter'}, status=400)

        try:
            doc = Doc.objects.get(doc_id=doc_id)
        except Doc.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Doc does not exist'}, status=404)

        request.doc_object = doc  # Attach doc to request object so that it's available in the view
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def require_prototype(view_func):
    def _wrapped_view(request, *args, **kwargs):
        prototype_id = request.GET.get('prototype_id')
        if not prototype_id:
            prototype_id = request.data.get('prototype_id')

        if not prototype_id:
            return JsonResponse({'status': 'error', 'message': 'Missing prototype_id parameter'}, status=400)

        try:
            prototype = Prototype.objects.get(prototype_id=prototype_id)
        except Prototype.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Prototype does not exist'}, status=404)

        request.prototype_object = prototype  # Attach prototype to request object so that it's available in the view
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def require_node(view_func):
    def _wrapped_view(request, *args, **kwargs):
        node_id = request.GET.get('node_id')
        if not node_id:
            node_id = request.data.get('node_id')

        if not node_id:
            return JsonResponse({'status': 'error', 'message': 'Missing node_id parameter'}, status=400)

        try:
            node = Node.objects.get(node_id=node_id)
        except Node.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Node does not exist'}, status=404)

        request.node_object = node  # Attach node to request object so that it's available in the view
        return view_func(request, *args, **kwargs)

    return _wrapped_view
