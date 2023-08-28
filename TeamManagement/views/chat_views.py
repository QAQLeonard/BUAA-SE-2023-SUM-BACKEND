import json
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from TeamManagement.models import Message, User, ChatGroup, GroupMember


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


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_groups(request):
    username = request.GET.get('username')
    if not username:
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

    # 获取用户对象
    user = User.objects.get(username=username)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User does not exist'})
    # 获取用户所在的所有群组
    group_members = GroupMember.objects.filter(user=user)
    groups = [gm.group for gm in group_members]

    # 将群组信息序列化为 JSON 格式
    data = []
    for group in groups:
        data.append({
            'group_id': group.group_id,
            'group_name': group.group_name,
            'group_type': group.group_type,
            'team_id': group.team.team_id,
        })

    return JsonResponse({'status': 'success', 'data': data})


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_group_messages(request):
    group_id = request.GET.get('group_id')
    if not group_id:
        return JsonResponse({'status': 'error', 'message': 'Missing group_id parameter'},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        group = ChatGroup.objects.get(group_id=group_id)
    except ChatGroup.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'ChatGroup does not exist'},
                            status=status.HTTP_404_NOT_FOUND)

    messages = Message.objects.filter(group=group).order_by('timestamp')

    if not messages:
        return JsonResponse({'status': 'error', 'message': 'No messages found'},
                            status=status.HTTP_400_BAD_REQUEST)

    messages_list = []
    for message in messages:
        messages_list.append({
            'message_id': message.message_id,
            'sender': message.sender.username,  # Assuming User model has a 'username' field
            'content': message.content,
            'timestamp': message.timestamp,
            'message_type': message.message_type
        })

    return JsonResponse({'status': 'success', 'data': messages_list}, status=status.HTTP_200_OK)