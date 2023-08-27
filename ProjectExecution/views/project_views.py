from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from ProjectExecution.models import Project
from ProjectExecution.serializers import ProjectSerializer

from TeamManagement.models import Team, TeamMember


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

    # 使用获取的数据创建新的Project对象
    project = Project(
        project_id=project_id,
        project_name=project_name,
        project_description=project_description,
        team=team,
        project_image=project_image
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
def update_project(request):
    data = request.data
    try:
        project = Project.objects.get(project_id=data.get('project_id'))
        team = Team.objects.get(team_id=data.get('team_id'))
    except (Project.DoesNotExist, Team.DoesNotExist):
        return Response({"status": "error", "message": "Project or Team does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    # 更新数据
    project.project_name = data.get('project_name', project.project_name)
    project.project_description = data.get('project_description', project.project_description)
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
def delete_project(request):
    project_id = request.data.get('project_id')

    try:
        project = Project.objects.get(project_id=project_id)
    except Project.DoesNotExist:
        return Response({"status": "error", "message": "Project does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    project.delete()

    return Response({"status": "success", "message": "Project Deleted"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_team_projects(request):
    team_id = request.GET.get('team_id')

    try:
        team = Team.objects.get(team_id=team_id)
    except Team.DoesNotExist:
        return Response({"status": "error", "message": "Team does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    # 验证请求用户是否为团队成员
    try:
        team_membership = TeamMember.objects.get(team=team, user=request.user)
    except TeamMember.DoesNotExist:
        return Response({"status": "error", "message": "You are not a member of this team"}, status=status.HTTP_403_FORBIDDEN)

    # 获取并返回该团队的所有项目
    projects = Project.objects.filter(team=team)
    project_data = [{"project_id": project.project_id, "project_name": project.project_name} for project in projects]

    return Response({"status": "success", "projects": project_data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_project(request):
    project_id = request.GET.get('project_id')
    if not project_id:
        return Response({"status": "error", "message": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        project = Project.objects.get(project_id=project_id)
    except Project.DoesNotExist:
        return Response({"status": "error", "message": "Project does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    response_data = {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "project_description": project.project_description,
        "team_id": project.team.team_id,
    }
    return Response({"status": "success", "project": response_data}, status=status.HTTP_200_OK)
