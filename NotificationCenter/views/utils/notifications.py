import json
import uuid
from django.utils import timezone
from NotificationCenter.models import Notification
from ProjectExecution.models import Doc
from TeamManagement.models import User, Message


def create_notification(json_str):
    try:
        notification_id = generate_notification_id()
        data = json.loads(json_str)
        username = data.get('username')
        user = User.objects.get(username=username)
        notification_type = data.get('notification_type')
        content = data.get('content')
        notification = None
        if notification_type == "document":
            doc_id = data.get('doc_id')
            doc = Doc.objects.get(doc_id=doc_id)
            notification = Notification.objects.create(
                notification_id=notification_id,
                user=user,
                notification_type=notification_type,
                content=content,
                doc=doc,
                created_at=timezone.now()
            )
        elif notification_type == "group_chat":
            message_id = data.get('message_id')
            message = Message.objects.get(message_id=message_id)
            notification = Notification.objects.create(
                notification_id=notification_id,
                user=user,
                notification_type=notification_type,
                content=content,
                message=message,
                created_at=timezone.now()
            )
        elif notification_type == "system":
            notification = Notification.objects.create(
                notification_id=notification_id,
                user=user,
                notification_type=notification_type,
                content=content,
                created_at=timezone.now()
            )

        return notification

    except Exception as e:
        print(e)
        return f'An error occurred: {e}'


def generate_notification_id():
    return str(uuid.uuid4())
