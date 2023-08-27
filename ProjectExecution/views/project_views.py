from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage
from ProjectExecution.models import Project
from ProjectExecution.serializers import ProjectSerializer
import os

from TeamManagement.models import Team


@api_view(['POST'])
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

        return Response(serializer.data, status=status.HTTP_201_CREATED)
