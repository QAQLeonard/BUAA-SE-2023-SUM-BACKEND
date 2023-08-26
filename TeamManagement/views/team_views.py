from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.forms import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, status
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import smtplib
import random
import json
from TeamManagement.models import *
from TeamManagement.serializers import *
from shared.utils.TeamManage.users import *
from shared.utils.email import send_email


class TeamCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = TeamSerializer


class TeamMemberCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_team_members(request):
    team_id = request.GET.get('team_id')  # Retrieve the team_id from the query parameters

    if not team_id:
        return JsonResponse({"status": "error", "message": "team_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        team = Team.objects.get(team_id=team_id)  # Retrieve the Team object based on the team_id
    except Team.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Team not found"}, status=status.HTTP_404_NOT_FOUND)

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

    serializer = TeamMemberSerializer(members_data, many=True)
    return JsonResponse({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)


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

    team = Team(team_id=team_id, team_name=team_name, team_description=team_description)
    team.save()

    # 创建默认群聊
    group_name = team_name + '默认群聊'
    group = ChatGroup(group_id=team_id, group_name=group_name, team=team)
    group.save()

    # 将创建者加入Team和ChatGroup
    user = request.user
    team_member = TeamMember(team=team, user=user, role='Creator')
    team_member.save()
    group_member = GroupMember(group=group, user=user)
    group_member.save()

    return JsonResponse({'status': 'success'}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_team_member(request):
    # 获取前端传入的JSON数据
    data = request.data

    # 获取通过Token验证的当前用户
    current_user = request.user

    # 获取团队ID和要添加的成员信息（电子邮件或用户名）
    team_id = data.get('team_id')
    email = data.get('email')
    username = data.get('username')

    # 验证数据完整性
    if not team_id or not (email or username):
        return JsonResponse({"status": "error", "message": "Incomplete data"}, status=status.HTTP_400_BAD_REQUEST)

    # 查找团队
    try:
        team = Team.objects.get(team_id=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Team not found"}, status=status.HTTP_404_NOT_FOUND)

    # 检查当前用户是否为团队成员
    is_member = TeamMember.objects.filter(team=team, user=current_user).exists()
    if not is_member:
        return JsonResponse({"status": "error", "message": "You are not a member of this team"},
                            status=status.HTTP_403_FORBIDDEN)

    # 查找要添加的用户
    user_to_add = None
    if email:
        try:
            user_to_add = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "User with this email not found"},
                                status=status.HTTP_404_NOT_FOUND)
    elif username:
        try:
            user_to_add = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "User with this username not found"},
                                status=status.HTTP_404_NOT_FOUND)

    # 检查用户是否已是团队成员
    already_member = TeamMember.objects.filter(team=team, user=user_to_add).exists()
    if already_member:
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
def remove_team_member(request):
    # 获取前端传入的JSON数据
    data = request.data

    # 获取通过Token验证的当前用户
    current_user = request.user

    # 获取团队ID和要删除的成员用户名
    team_id = data.get('team_id')
    username_to_remove = data.get('username')

    # 验证数据完整性
    if not team_id or not username_to_remove:
        return JsonResponse({"status": "error", "message": "Incomplete data"}, status=status.HTTP_400_BAD_REQUEST)

    # 查找团队
    try:
        team = Team.objects.get(team_id=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Team not found"}, status=status.HTTP_404_NOT_FOUND)

    # 查找要删除的用户
    try:
        user_to_remove = User.objects.get(username=username_to_remove)
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User to remove not found"},
                            status=status.HTTP_404_NOT_FOUND)

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
def get_user_role_in_team(request):
    team_id = request.GET.get('team_id')
    username = request.GET.get('username')

    if not team_id or not username:
        return JsonResponse(
            {"status": "error", "message": "Both team_id and username are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        team = Team.objects.get(team_id=team_id)
    except Team.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Team not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

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
def set_team_member_role(request):
    data = request.data
    current_user = request.user

    team_id = data.get('team_id')
    target_username = data.get('username')
    new_role = data.get('role')

    # Verify the data
    if not all([team_id, target_username, new_role]):
        return JsonResponse({"status": "error", "message": "Incomplete data"}, status=status.HTTP_400_BAD_REQUEST)

    # Make sure the new role is either 'Admin' or 'Member'
    if new_role not in ['Admin', 'Member']:
        return JsonResponse({"status": "error", "message": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

    # Verify the team exists
    try:
        team = Team.objects.get(team_id=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Team not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if the current user is an admin or the creator of the team
    try:
        current_member = TeamMember.objects.get(team=team, user=current_user)
        if current_member.role not in ['Admin', 'Creator'] or (current_member.role == 'Admin' and new_role == 'Admin'):
            return JsonResponse({"status": "error", "message": "You don't have permission to change roles"},
                                status=status.HTTP_403_FORBIDDEN)
    except TeamMember.DoesNotExist:
        return JsonResponse({"status": "error", "message": "You are not a member of this team"},
                            status=status.HTTP_403_FORBIDDEN)

    # Get the target member
    try:
        target_member = TeamMember.objects.get(team=team, user__username=target_username)
    except TeamMember.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Target member not found"}, status=status.HTTP_404_NOT_FOUND)

    # You can't change the role of the team creator
    if target_member.role == 'Creator':
        return JsonResponse({"status": "error", "message": "Cannot change the role of the team creator"},
                            status=status.HTTP_403_FORBIDDEN)

    # Update the role
    target_member.role = new_role
    target_member.save()

    return JsonResponse({"status": "success", "message": f"Successfully updated role to {new_role}"},
                        status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_teams(request):
    username = request.GET.get('username', None)
    if username is None:
        return JsonResponse({'error': 'Username parameter is missing'}, status=400)

    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    teams = user.teams.all()
    team_names = [team.name for team in teams]

    return JsonResponse({'teams': team_names})


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_teams(request):
    username = request.GET.get('username', None)

    if username is None:
        return JsonResponse({"status": "error", "message": "Username parameter is missing"},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User not found"},
                            status=status.HTTP_404_NOT_FOUND)

    team_memberships = TeamMember.objects.filter(user=user).select_related('team')  # 使用 select_related 获取关联的 Team 对象
    serialized_data = []
    for membership in team_memberships:
        team_data = TeamSerializer(membership.team).data  # 使用 TeamSerializer 序列化 Team 对象
        member_data = TeamMemberSerializer(membership).data  # 使用 TeamMemberSerializer 序列化 TeamMember 对象
        team_data['role'] = member_data['role']  # 添加角色信息到 team 数据中
        serialized_data.append(team_data)

    return JsonResponse({"status": "success", "message": "Teams retrieved", "data": serialized_data},
                        status=status.HTTP_200_OK)
