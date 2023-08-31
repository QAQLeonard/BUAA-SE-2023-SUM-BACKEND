import pytz
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from ProjectExecution.serializers import ProjectSerializer

from TeamManagement.models import Notification
from TeamManagement.serializers import NotificationSerializer
from TeamManagement.views import require_team


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_notifications(request):
    user = request.user
    require_type = request.GET.get('require_type')
    notifications = None
    if require_type == 'ALL':
        notifications = Notification.objects.filter(user=user)

    elif require_type == '@':
        notifications = Notification.objects. \
            filter(Q(user=user) & (Q(notification_type='group_chat') | Q(notification_type='document')))

    elif require_type == 'system':
        notifications = Notification.objects.filter(user=user, notification_type='system')

    serializer = NotificationSerializer(notifications, many=True)
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_notification(request):
    notification_id = request.GET.get('notification_id')
    is_read = request.GET.get('is_read')
    notification = Notification.objects.get(notification_id=notification_id)
    notification.is_read = is_read
    notification.save()
    return Response({"status": "success"}, status=status.HTTP_200_OK)
