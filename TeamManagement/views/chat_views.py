import json
import uuid

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
import re

from NotificationCenter.models import Notification
from TeamManagement.models import *
from TeamManagement.views.decorators import require_group
from shared.decorators import require_user, require_team


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_user
def get_group(request):
    group = request.group_object
    if group.group_type == 'Team':
        return JsonResponse({
            "status": "success",
            "data": {
                "group_id": group.group_id,
                "group_name": group.group_name,
                "group_type": group.group_type,
                "team_id": group.team.team_id,
            }
        })
    elif group.group_type == 'Public':
        return JsonResponse({
            "status": "success",
            "data": {
                "group_id": group.group_id,
                "group_name": group.group_name,
                "group_type": group.group_type,
            }
        })
    elif group.group_type == 'Private':
        partner_name = group.group_id.replace(request.user_object.username, '').replace('private_chat_', '').replace('_', '')
        return JsonResponse({
            "status": "success",
            "data": {
                "group_id": group.group_id,
                "group_name": partner_name,
                "group_type": group.group_type,
            }
        })


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_public_group(request):
    group_id = str(uuid.uuid4())
    data = request.data
    group_name = data.get('group_name')
    if not group_name:
        return JsonResponse({"status": "error", "message": "Missing required fields"})

    group = ChatGroup(
        group_id=group_id,
        group_name=group_name,
        group_type='Public',
        team=None
    )
    group.save()
    # Add the creator to the group
    group_member = GroupMember(
        group=group,
        user=request.user,
        role='Creator'
    )
    group_member.save()
    return JsonResponse({
        "status": "success",
        "message": "Group created successfully",
        "group_id": group_id
    })


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_user
def create_private_chat(request):
    creator = request.user
    dest_user = request.user_object
    if creator == dest_user:
        return JsonResponse({"status": "error", "message": "You cannot create a private chat with yourself"},
                            status=status.HTTP_400_BAD_REQUEST)
    # Check if the private chat already exists
    # existing_groups = ChatGroup.objects.filter(group_type='Private')
    # for group in existing_groups:
    #     if GroupMember.objects.filter(group=group, user=creator).exists() and \
    #             GroupMember.objects.filter(group=group, user=dest_user).exists():
    #         return JsonResponse({
    #             "status": "error",
    #             "message": "Private chat already exists"
    #             "group_id":
    #
    #         })
    # Create a new private chat
    usernames = sorted([creator.username, dest_user.username])
    if ChatGroup.objects.filter(group_id=f"private_chat_{usernames[0]}_{usernames[1]}").exists():
        return JsonResponse({
            "status": "error",
            "message": "Private chat already exists",
            "group_id": f"private_chat_{usernames[0]}_{usernames[1]}"
        })

    new_group = ChatGroup.objects.create(
        group_id=f"private_chat_{usernames[0]}_{usernames[1]}",
        group_name=f"{creator.username} and {dest_user.username}",
        group_type='Private',
        team=None
    )
    GroupMember.objects.create(group=new_group, user=creator)
    GroupMember.objects.create(group=new_group, user=dest_user)
    return JsonResponse({
        "status": "success",
        "message": "Private chat created successfully",
        "group_id": new_group.group_id,
    })


@csrf_exempt
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
            return JsonResponse({"status": "error", "message": "Missing required fields"})

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

        pattern = r'\/@\/(\w+)\s'
        mentioned_usernames = re.findall(pattern, content)
        if mentioned_usernames:
            for username in mentioned_usernames:
                if User.objects.filter(username=username).exists():
                    mentioned_user = User.objects.get(username=username)
                    Notification.objects.create(
                        user=mentioned_user,
                        notification_type='group_chat',
                        message=message,
                        content=f"你被 {sender_uname} 提及了",
                    )

        return JsonResponse({'status': 'success', "message": "Message saved successfully"})

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"})

    except Exception as e:
        return JsonResponse({"status": "error", 'message': str(e)})


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_user
def get_user_groups(request):
    user = request.user_object
    group_members = GroupMember.objects.filter(user=user)
    groups = [gm.group for gm in group_members]

    data = []
    for group in groups:
        if group.group_type == 'Team':
            data.append({
                'group_id': group.group_id,
                'group_name': group.group_name,
                'group_type': group.group_type,
                'team_id': group.team.team_id,
            })
        elif group.group_type == 'Public':
            data.append({
                'group_id': group.group_id,
                'group_name': group.group_name,
                'group_type': group.group_type,
            })
        elif group.group_type == 'Private':
            partner_name = group.group_id.replace(user.username, '').replace('private_chat_', '').replace('_', '')
            data.append({
                'group_id': group.group_id,
                'group_name': partner_name,
                'group_type': group.group_type,
            })

    return JsonResponse({'status': 'success', 'data': data})


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_group
def get_group_messages(request):
    messages = Message.objects.filter(group=request.group_object).order_by('timestamp')
    messages_list = []
    for message in messages:
        messages_list.append({
            'message_id': message.message_id,
            'sender_uname': message.sender.username,  # Assuming User model has a 'username' field
            'content': message.content,
            'timestamp': message.timestamp,
            'message_type': message.message_type
        })

    return JsonResponse({'status': 'success', 'data': messages_list}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_group
def get_group_members(request):
    members = GroupMember.objects.filter(group=request.group_object)
    members_list = []
    for member in members:
        members_list.append({
            'username': member.user.username,
            'email': member.user.email,
            'role': member.role
        })

    return JsonResponse({'status': 'success', 'data': members_list}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_group
def delete_group(request):
    group = request.group_object
    if group.group_type == 'Team':
        return JsonResponse({'status': 'error', 'message': 'Cannot delete team group'}, status=status.HTTP_403_FORBIDDEN)
    group.delete()
    return JsonResponse({'status': 'success', 'message': 'Group deleted successfully'}, status=status.HTTP_200_OK)