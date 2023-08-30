from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from ProjectExecution.models import Project, Doc
from ProjectExecution.serializers import ProjectSerializer
from ProjectExecution.views import *
from ProjectExecution.views.decorators import require_doc

from TeamManagement.models import Team, TeamMember, User


# 创建文档
@csrf_exempt
@api_view(['POST'])
@require_project
def create_doc(request):
    doc_id = request.data.get('doc_id')
    project = request.project_object
    doc_name = request.data.get('doc_name')

    # 校验参数
    if not doc_id or not doc_name:
        print("Missing required fields")
        return JsonResponse({"status": "error", "message": "Missing required fields"},
                            status=status.HTTP_400_BAD_REQUEST)
    if Doc.objects.filter(doc_id=doc_id).exists():
        print("Doc already exists")
        return JsonResponse({"status": "error", "message": "Doc already exists"},
                            status=status.HTTP_400_BAD_REQUEST)

    doc = Doc(doc_id=doc_id, project=project, doc_name=doc_name)
    doc.save()
    return JsonResponse({"status": "success", "message": "Document created"}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['DELETE'])
@require_doc
def delete_doc(request):
    doc = request.doc_object
    doc.delete()
    return JsonResponse({"status": "success", "message": "Document deleted"}, status=status.HTTP_200_OK)


# 修改文档权限
@csrf_exempt
@api_view(['PUT'])
def update_doc_permissions(request):
    editable_by_guests = request.data.get('editable_by_guests')
    doc = request.doc_object
    if editable_by_guests is None:
        return JsonResponse({"status": "error", "message": "Missing required fields"},
                            status=status.HTTP_400_BAD_REQUEST)
    doc.editable_by_guests = editable_by_guests
    doc.save()
    return JsonResponse({"status": "success", "message": "Document permissions updated"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@require_doc
def get_doc_permissions(request):
    doc = request.doc_object
    ebg = doc.editable_by_guests
    username = request.GET.get('username')
    if not username:
        if not ebg:
            print("You are not allowed to edit this doc")
            return JsonResponse({"status": "error", "message": "You are not allowed to edit this doc"},
                                status=status.HTTP_200_OK)
        else:
            return JsonResponse({"status": "success", "message": "You are allowed to edit this doc"},
                                status=status.HTTP_200_OK)
    else:
        user = User.objects.get(username=username)
        team = doc.project.team
        if not TeamMember.objects.filter(team=team, user=user).exists() and not ebg:
            return JsonResponse({"status": "error", "message": "You are not allowed to edit this doc"},
                                status=status.HTTP_200_OK)
        else:
            return JsonResponse({"status": "success", "message": "You are allowed to edit this doc"},
                                status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@require_project
def get_project_docs(request):
    project = request.project_object
    # 获取与特定项目相关的所有文档
    docs = Doc.objects.filter(project=project)
    # 将结果序列化为 JSON 格式
    doc_list = []
    for doc in docs:
        doc_list.append({
            'doc_id': doc.doc_id,
            'doc_name': doc.doc_name,
            'editable_by_guests': doc.editable_by_guests
        })

    return JsonResponse({"status": "success", "data": doc_list}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@require_doc
def get_doc_team_id(request):
    doc = request.doc_object
    team = doc.project.team
    return JsonResponse({"status": "success", "team_id": team.team_id},
                        status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET'])
@require_doc
def get_doc(request):
    doc = request.doc_object
    team = doc.project.team
    response_data = {
        'doc_id': doc.doc_id,
        'doc_name': doc.doc_name,
        'project_id': doc.project.project_id,
        'team_id': team.team_id,
        'editable_by_guests': doc.editable_by_guests,
    }
    return JsonResponse({"status": "success", "data": response_data}, status=status.HTTP_200_OK)
