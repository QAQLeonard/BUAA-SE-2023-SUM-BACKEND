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

from TeamManagement.models import Team


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_project(request):
    data = request.data

    try:
        team = Team.objects.get(team_id=data.get('team_id'))
    except Team.DoesNotExist:
        return Response({"error": "Team does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    # 使用序列化器验证数据
    serializer = ProjectSerializer(data=data)

    if serializer.is_valid():
        serializer.validated_data['team'] = team
        # 保存数据到数据库
        project = serializer.save()

        # 重命名并保存图片文件
        if 'project_image' in request.FILES:
            old_file = project.project_image
            new_filename = f"{project.project_id}_image.png"

            new_file = ContentFile(old_file.read())
            new_file.name = new_filename

            project.project_image.delete(save=False)  # 删除旧文件
            project.project_image.save(new_filename, new_file, save=True)  # 保存新文件

    return Response({"status": "success", "message": "Project Created"}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_project(request):
    try:
        project_id = request.data.get('project_id')
        project = Project.objects.get(project_id=project_id)
    except Project.DoesNotExist:
        return Response({"status": "error", "message": "Project does not exist"}, status=status.HTTP_404_NOT_FOUND)

    team_id = request.data.get('team_id')
    try:
        team = Team.objects.get(team_id=team_id)
    except Team.DoesNotExist:
        return Response({"status": "error", "message": "Team does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ProjectSerializer(project, data=request.data)

    if serializer.is_valid():
        serializer.validated_data['team'] = team
        serializer.save()

        # Rename and save image file
        if 'project_image' in request.FILES:
            old_file = project.project_image
            new_filename = f"{project.project_id}_image.png"

            new_file = ContentFile(old_file.read())
            new_file.name = new_filename

            project.project_image.delete(save=False)
            project.project_image.save(new_filename, new_file, save=True)

        return Response({"status": "success", "message": "Project Updated"}, status=status.HTTP_200_OK)
    return Response({"status": "error", "message": "Unknown"}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_project(request):
    try:
        project_id = request.data.get('project_id')
        project = Project.objects.get(project_id=project_id)
    except Project.DoesNotExist:
        return Response({"status": "error", "message": "Project does not exist"}, status=status.HTTP_404_NOT_FOUND)

    project.delete()
    return Response({"status": "success", "message": "Project deleted"}, status=status.HTTP_204_NO_CONTENT)