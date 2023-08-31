from django.forms import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets, status
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
import json
from TeamManagement.serializers import *
from TeamManagement.views.decorators import *
from shared.decorators import *
from shared.utils.TeamManage.users import *


class TeamCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = TeamSerializer


class TeamMemberCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberUserSerializer


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_team
def get_team_members(request):
    team = request.team_object

    members = TeamMember.objects.filter(team=team)  # Query TeamMember objects using the Team object

    if not members.exists():
        return JsonResponse({"status": "error", "message": "No members found for this team"},
                            status=status.HTTP_404_NOT_FOUND)

    members_data = []
    for member in members:
        member_data = model_to_dict(member)
        member_data['user'] = model_to_dict(User.objects.get(username=member.user.username))
        member_data['role'] = member.role  # Add the role information
        members_data.append(member_data)

    serializer = TeamMemberUserSerializer(members_data, many=True)

    flat_data = []
    for item in serializer.data:
        flat_item = {**item['user'], 'role': item['role']}
        flat_data.append(flat_item)

    return JsonResponse({"status": "success", "data": flat_data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_team(request):
    data = json.loads(request.body.decode('utf-8'))
    team_name = data.get('team_name')
    team_description = data.get('team_description')
    team_id = data.get('team_id')
    if not team_name or not team_description or not team_id:
        return JsonResponse({"status": "error", "message": "team_name, team_description and team_id are required"},
                            status=status.HTTP_400_BAD_REQUEST)

    team = Team.objects.filter(team_id=team_id)
    if team.exists():
        return JsonResponse({"status": "error", "message": "Team already exists"}, status=status.HTTP_409_CONFLICT)

    team = Team(team_id=team_id, team_name=team_name, team_description=team_description, tag='Team')
    team.save()

    # 创建默认群聊
    group_name = team_name + '_DefaultChatGroup'
    group = ChatGroup(group_id=team_id+"_default", group_name=group_name, team=team)
    group.save()

    # 将创建者加入Team和ChatGroup
    user = request.user
    team_member = TeamMember(team=team, user=user, role='Creator')
    team_member.save()
    group_member = GroupMember(group=group, user=user, role='Creator')
    group_member.save()

    return JsonResponse({'status': 'success'}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_team
@require_user
def add_team_member(request):
    # 获取通过Token验证的当前用户
    current_user = request.user
    team = request.team_object
    user_to_add = request.user_object

    # 检查当前用户是否为团队成员
    if not TeamMember.objects.filter(team=team, user=current_user).exists():
        return JsonResponse({"status": "error", "message": "You are not a member of this team"},
                            status=status.HTTP_403_FORBIDDEN)
    # 检查用户是否已是团队成员
    if TeamMember.objects.filter(team=team, user=user_to_add).exists():
        return JsonResponse({"status": "error", "message": "User is already a member of this team"},
                            status=status.HTTP_400_BAD_REQUEST)
    # 添加用户到团队
    TeamMember.objects.create(team=team, user=user_to_add)
    GroupMember.objects.create(group=ChatGroup.objects.get(team=team), user=user_to_add)

    return JsonResponse({'status': 'success', "message": "User successfully added to the team"},
                        status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_team
@require_user
def remove_team_member(request):
    # 获取通过Token验证的当前用户
    current_user = request.user
    # 获取团队ID和要删除的成员用户名
    team = request.team_object
    user_to_remove = request.user_object

    # 获取当前用户和要删除用户的团队成员信息
    try:
        current_team_member = TeamMember.objects.get(team=team, user=current_user)
        team_member_to_remove = TeamMember.objects.get(team=team, user=user_to_remove)
    except TeamMember.DoesNotExist:
        return JsonResponse({"status": "error", "message": "One or both users are not members of this team"},
                            status=status.HTTP_404_NOT_FOUND)
    # 检查删除权限
    if current_team_member.role == 'Creator':
        if team_member_to_remove.role == 'Creator':
            return JsonResponse({"status": "error", "message": "Cannot remove the Creator of the team"},
                                status=status.HTTP_403_FORBIDDEN)
    elif current_team_member.role == 'Admin':
        if team_member_to_remove.role != 'Member':
            return JsonResponse({"status": "error", "message": "Admin can only remove Members"},
                                status=status.HTTP_403_FORBIDDEN)
    else:
        return JsonResponse({"status": "error", "message": "You don't have permission to remove members"},
                            status=status.HTTP_403_FORBIDDEN)

    # 删除团队成员
    team_member_to_remove.delete()
    group_member_to_remove = GroupMember.objects.get(group=ChatGroup.objects.get(team=team), user=user_to_remove)
    group_member_to_remove.delete()

    return JsonResponse({"status": "success", "message": "Member successfully removed from the team"},
                        status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_team
@require_user
def get_user_role_in_team(request):
    team = request.team_object
    user = request.user_object
    try:
        team_member = TeamMember.objects.get(team=team, user=user)
        role = team_member.role
    except TeamMember.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "User is not a member of this team"},
            status=status.HTTP_404_NOT_FOUND
        )
    return JsonResponse({"status": "success", "role": role}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_team
@require_user
def set_team_member_role(request):
    current_user = request.user

    team = request.team_object
    target_user = request.user_object
    new_role = request.data.get('role')

    # Verify the data
    if not new_role:
        return JsonResponse({"status": "error", "message": "Incomplete data"}, status=status.HTTP_400_BAD_REQUEST)
    # Make sure the new role is either 'Admin' or 'Member'
    if new_role not in ['Admin', 'Member']:
        return JsonResponse({"status": "error", "message": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the current user is an admin or the creator of the team
    try:
        current_member = TeamMember.objects.get(team=team, user=current_user)
        if current_member.role not in ['Admin', 'Creator']:
            return JsonResponse({"status": "error", "message": "You don't have permission to change roles"},
                                status=status.HTTP_403_FORBIDDEN)
    except TeamMember.DoesNotExist:
        return JsonResponse({"status": "error", "message": "You are not a member of this team"},
                            status=status.HTTP_403_FORBIDDEN)

    # Get the target member
    try:
        target_member = TeamMember.objects.get(team=team, user=target_user)
    except TeamMember.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Target member not found"}, status=status.HTTP_404_NOT_FOUND)

    # You can't change the role of the team creator
    if target_member.role == 'Creator':
        return JsonResponse({"status": "error", "message": "Cannot change the role of the team creator"},
                            status=status.HTTP_403_FORBIDDEN)
    if target_member.role == 'Admin' and new_role == 'Member' and current_member.role != 'Creator':
        return JsonResponse({"status": "error", "message": "Only the creator can change an admin to a member"},
                            status=status.HTTP_403_FORBIDDEN)
    # Update the role
    target_member.role = new_role
    target_group_member = GroupMember.objects.get(group=ChatGroup.objects.get(team=team), user=target_user)
    target_group_member.role = new_role
    target_member.save()
    target_group_member.save()

    return JsonResponse({"status": "success", "message": f"Successfully updated role to {new_role}"},
                        status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_user
def get_user_teams(request):
    user = request.user_object

    # 从TeamMember模型中获取该用户所有的团队信息
    team_memberships = TeamMember.objects.filter(user=user)

    # 使用嵌套的TeamMemberTeamSerializer来进行序列化
    serializer = TeamMemberTeamSerializer(team_memberships, many=True)

    flat_data = []
    for item in serializer.data:
        flat_item = {**item['team'], 'role': item['role']}
        flat_data.append(flat_item)

    return JsonResponse({"status": "success", "data": flat_data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_team
def get_team(request):
    team = request.team_object
    serializer = TeamSerializer(team)
    return JsonResponse({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
