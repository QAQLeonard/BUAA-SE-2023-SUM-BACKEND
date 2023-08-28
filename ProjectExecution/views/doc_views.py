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

from TeamManagement.models import Team, TeamMember, User


# 创建文档
@csrf_exempt
@api_view(['POST'])
def create_doc(request):
    doc_id = request.data.get('doc_id')
    project_id = request.data.get('project_id')

    # 校验参数
    if not doc_id or not project_id:
        return JsonResponse({"status": "error", "message": "Missing required fields"},
                            status=status.HTTP_400_BAD_REQUEST)
    if Doc.objects.filter(doc_id=doc_id).exists():
        return JsonResponse({"status": "error", "message": "Doc already exists"},
                            status=status.HTTP_400_BAD_REQUEST)
    if not Project.objects.filter(project_id=project_id).exists():
        return JsonResponse({"status": "error", "message": "Project does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)
    project = Project.objects.get(project_id=project_id)

    doc = Doc(doc_id=doc_id, project=project)
    doc.save()
    return JsonResponse({"status": "success", "message": "Document created"}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['DELETE'])
def delete_doc(request):
    doc_id = request.GET.get('doc_id')
    if not doc_id:
        return JsonResponse({"status": "error", "message": "Missing doc_id parameter"},
                            status=status.HTTP_400_BAD_REQUEST)
    if not Doc.objects.filter(doc_id=doc_id).exists():
        return JsonResponse({"status": "error", "message": "Doc does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)
    doc = Doc.objects.get(doc_id=doc_id)
    doc.delete()
    return JsonResponse({"status": "success", "message": "Document deleted"}, status=status.HTTP_200_OK)


# 修改文档权限
@csrf_exempt
@api_view(['PUT'])
def update_doc_permissions(request):
    editable_by_guests = request.data.get('editable_by_guests')
    doc_id = request.data.get('doc_id')
    if editable_by_guests is None or not doc_id:
        return JsonResponse({"status": "error", "message": "Missing required fields"},
                            status=status.HTTP_400_BAD_REQUEST)
    if not Doc.objects.filter(doc_id=doc_id).exists():
        return JsonResponse({"status": "error", "message": "Doc does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)
    doc = Doc.objects.get(doc_id=doc_id)
    doc.editable_by_guests = editable_by_guests
    doc.save()

    return JsonResponse({"status": "success", "message": "Document permissions updated"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def get_doc_permissions(request):
    doc_id = request.GET.get('doc_id')
    if not doc_id:
        return JsonResponse({"status": "error", "message": "Missing doc_id parameter"},
                            status=status.HTTP_400_BAD_REQUEST)
    if not Doc.objects.filter(doc_id=doc_id).exists():
        return JsonResponse({"status": "error", "message": "Doc does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)
    doc = Doc.objects.get(doc_id=doc_id)
    ebg = doc.editable_by_guests
    username = request.GET.get('username')
    if not username and not ebg:
        return JsonResponse({"status": "error", "message": "You are not allowed to edit this doc"},
                            status=status.HTTP_400_BAD_REQUEST)
    elif not username and ebg:
        return JsonResponse({"status": "success", "message": "You are allowed to edit this doc"},
                            status=status.HTTP_200_OK)
    if not User.objects.filter(username=username).exists():
        return JsonResponse({"status": "error", "message": "User does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(username=username)
    team = doc.project.team
    if not TeamMember.objects.filter(team=team, user=user).exists() and not ebg:
        return JsonResponse({"status": "error", "message": "You are not allowed to edit this doc"},
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"status": "success", "message": "You are allowed to edit this doc"},
                            status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
def get_project_docs(request):
    project_id = request.GET.get('project_id')
    if not project_id:
        return JsonResponse({"status": "error", "message": "Missing project_id parameter"},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        project = Project.objects.get(project_id=project_id)
    except Project.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Project does not exist"},
                            status=status.HTTP_404_NOT_FOUND)

    # 获取与特定项目相关的所有文档
    docs = Doc.objects.filter(project=project)

    # 将结果序列化为 JSON 格式
    doc_list = []
    for doc in docs:
        doc_list.append({
            'doc_id': doc.doc_id,
            'editable_by_guests': doc.editable_by_guests
        })

    return JsonResponse({"status": "success", "data": doc_list}, status=status.HTTP_200_OK)

