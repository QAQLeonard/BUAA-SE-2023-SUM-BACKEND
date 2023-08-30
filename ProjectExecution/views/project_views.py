import pytz
from django.core.files.base import ContentFile
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from ProjectExecution.models import Project
from ProjectExecution.serializers import ProjectSerializer
from ProjectExecution.views.decorators import require_project

from TeamManagement.models import Team, TeamMember
from TeamManagement.views import require_team


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_project(request):
    try:
        # 从请求数据中获取信息
        data = request.data
        team_id = data.get('team_id')
        project_id = data.get('project_id')
        project_name = data.get('project_name')
        project_description = data.get('project_description')
        project_image = request.FILES.get('project_image', None)

        # 根据team_id获取Team对象
        team = Team.objects.get(team_id=team_id)

    except Team.DoesNotExist:
        return Response({"status": "error", "message": "Team does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    current_time_utc = timezone.now()
    local_timezone = pytz.timezone('Asia/Shanghai')
    current_time_local = current_time_utc.astimezone(local_timezone)
    created_at = current_time_local
    # 使用获取的数据创建新的Project对象
    project = Project(
        project_id=project_id,
        project_name=project_name,
        project_description=project_description,
        team=team,
        project_image=project_image,
        created_at=created_at
    )

    # 保存Project对象到数据库
    project.save()

    # 如果需要，你可以在这里进行额外的处理，比如图片文件重命名
    if project_image:
        new_filename = f"{project.project_id}_image.png"

        new_file = ContentFile(project.project_image.read())
        new_file.name = new_filename

        project.project_image.delete(save=False)  # 删除旧文件
        project.project_image.save(new_filename, new_file, save=True)  # 保存新文件

    return Response({"status": "success", "message": "Project Created"}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_project
@require_team
def update_project(request):
    project = request.project_object
    team = request.team_object

    # 更新数据
    project.project_name = request.data.get('project_name', project.project_name)
    project.project_description = request.data.get('project_description', project.project_description)
    project.team = team

    # 处理图片
    if 'project_image' in request.FILES:
        old_file = project.project_image
        new_filename = f"{project.project_id}_image.png"

        new_file = ContentFile(old_file.read())
        new_file.name = new_filename

        project.project_image.delete(save=False)  # 删除旧文件
        project.project_image.save(new_filename, new_file, save=True)  # 保存新文件

    project.save()

    return Response({"status": "success", "message": "Project Updated"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_project
def delete_project(request):
    project = request.project_object
    if project.tag == 'Deleted':
        if project.project_image:
            project.project_image.delete(save=False)
        project.delete()
        return Response({"status": "success", "message": "Project Removed Completely"}, status=status.HTTP_200_OK)
    else:
        project.tag = 'Deleted'
        project.save()
        return Response({"status": "success", "message": "Project Removed"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_project
def restore_project(request):
    project = request.project_object
    if project.tag != 'Deleted':
        return Response({"status": "error", "message": "Project is not deleted"}, status=status.HTTP_400_BAD_REQUEST)
    project.tag = 'Normal'
    project.save()
    return Response({"status": "success", "message": "Project Restored"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_team
def get_team_projects(request):
    team = request.team_object
    tag = request.GET.get('tag')
    # 验证请求用户是否为团队成员

    try:
        team_membership = TeamMember.objects.get(team=team, user=request.user)
    except TeamMember.DoesNotExist:
        return Response({"status": "error", "message": "You are not a member of this team"},
                        status=status.HTTP_403_FORBIDDEN)

    # 获取并返回该团队的所有项目
    projects = Project.objects.filter(team=team, tag=tag).order_by('-created_at')
    project_data = [{"project_id": project.project_id, "project_name": project.project_name,
                     "created_at": project.created_at} for project in projects]

    return Response({"status": "success", "projects": project_data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_project
def get_project(request):
    project = request.project_object
    response_data = {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "project_description": project.project_description,
        "team_id": project.team.team_id,
        "tag": project.tag,
        "created_at": project.created_at,
    }
    return Response({"status": "success", "project": response_data}, status=status.HTTP_200_OK)
