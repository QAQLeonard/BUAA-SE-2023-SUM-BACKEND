import json
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from TeamManagement.models import Message, User, ChatGroup


@csrf_exempt  # 注意：在生产环境中，你应该使用更安全的方法来处理 CSRF。
@api_view(['POST'])
def save_message(request):
    try:
        data = request.data
        content = data.get('content')
        sender_uname = data.get('sender_uname')
        group_id = data.get('group_id')
        timestamp = timezone.now()
        now_str = timezone.now().strftime('%Y%m%d%H%M%S')

        if not all([content, sender_uname, group_id]):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        # 保存消息到数据库
        message = Message(
            content=content,
            sender=User.objects.get(username=sender_uname),  # 你可以使用 username 或者 email 来获取用户对象
            group=ChatGroup.objects.get(group_id=group_id),
            timestamp=timestamp,
            message_type='Text',
            message_id=f"{group_id}{sender_uname}{now_str}"
        )
        message.save()

        return JsonResponse({'status': 'success', 'message': 'Message saved successfully'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
