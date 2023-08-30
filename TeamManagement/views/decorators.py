from functools import wraps
from django.http import JsonResponse

from TeamManagement.models import *


def require_group(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        group_id = request.GET.get('group_id')
        if not group_id:
            group_id = request.data.get('group_id')

        if not group_id:
            return JsonResponse({'status': 'error', 'message': 'Missing group_id parameter'}, status=400)

        try:
            group = ChatGroup.objects.get(group_id=group_id)
        except ChatGroup.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'ChatGroup does not exist'}, status=404)

        request.group_object = group  # Attach group to request object so that it's available in the view
        return view_func(request, *args, **kwargs)
    return _wrapped_view



