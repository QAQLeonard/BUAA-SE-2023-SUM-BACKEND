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
    team_id = request.GET.get('team_id')  # Change to match the updated field name in the model

    if not team_id:
        return JsonResponse({'status': 'error', 'message': 'team_id is required'})

    members = TeamMember.objects.filter(team_id=team_id)  # Change to match the updated field name in the model

    if not members.exists():
        return JsonResponse({'status': 'error', 'message': 'Team not found'})

    members_data = []
    for member in members:
        member_data = model_to_dict(member)
        member_data['user'] = model_to_dict(
            User.objects.get(username=member.username))  # Assume 'id' is the primary key for User
        members_data.append(member_data)

    serializer = UserSerializer(members_data, many=True)
    return JsonResponse({'status': 'success', 'data': serializer.data})


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_team(request):
    data = json.loads(request.body.decode('utf-8'))
    team_name = data.get('team_name')
    team_description = data.get('team_description')
    team_id = data.get('team_id')
    if not team_name or not team_description or not team_id:
        return JsonResponse({'status': 'error', 'message': 'team_name, team_description and team_id are required'})

    team = Team.objects.filter(team_id=team_id)
    if team.exists():
        return JsonResponse({'status': 'error', 'message': 'Team already exists'})

    team = Team(team_id=team_id, team_name=team_name, team_description=team_description)
    team.save()

    # 创建默认群聊
    group_name = team_name + '默认群聊'
    group = ChatGroup(group_id=team_id, group_name=group_name, team=team)
    group.save()
    return JsonResponse({'status': 'success'})
