from functools import wraps

from django.db.models import Q
from django.http import JsonResponse
from rest_framework import status

from TeamManagement.models import *


def require_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        username = request.GET.get('username')
        if not username:
            username = request.data.get('username')

        email = request.GET.get('email')
        if not email:
            email = request.data.get('email')

        query = Q()
        if username:
            query |= Q(username=username)
        if email:
            query |= Q(email=email)

        if not query:
            return JsonResponse({"status": "error", "message": "Parameter is required"},
                                status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(query).exists():
            return JsonResponse({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(query)
        request.user_object = user  # Attach user to request object so that it's available in the view
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def require_team(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        team_id = request.GET.get('team_id')
        if not team_id:
            team_id = request.data.get('team_id')

        if not team_id:
            return JsonResponse({'status': 'error', 'message': 'Missing team_id parameter'}, status=400)

        try:
            team = Team.objects.get(team_id=team_id)
        except Team.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Team does not exist'}, status=404)

        request.team_object = team  # Attach team to request object so that it's available in the view
        return view_func(request, *args, **kwargs)
    return _wrapped_view
