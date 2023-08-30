from functools import wraps
from django.http import JsonResponse

from TeamManagement.models import *


def require_group(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        group_id = request.GET.get('group_id')
        if not group_id:
            return JsonResponse({'status': 'error', 'message': 'Missing group_id parameter'}, status=400)

        try:
            group = ChatGroup.objects.get(group_id=group_id)
        except ChatGroup.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'ChatGroup does not exist'}, status=404)

        request.group = group  # Attach group to request object so that it's available in the view
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def require_team(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        team_id = request.GET.get('team_id')
        if not team_id:
            return JsonResponse({'status': 'error', 'message': 'Missing team_id parameter'}, status=400)

        try:
            team = Team.objects.get(team_id=team_id)
        except Team.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Team does not exist'}, status=404)

        request.team = team  # Attach team to request object so that it's available in the view
        return view_func(request, *args, **kwargs)
    return _wrapped_view
