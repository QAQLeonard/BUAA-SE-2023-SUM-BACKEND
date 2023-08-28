from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from ProjectExecution.models import Project, Prototype
from ProjectExecution.serializers import ProjectSerializer, PrototypeSerializer

from TeamManagement.models import Team, TeamMember


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_prototype(request):
    data = request.data

    try:
        project = Project.objects.get(project_id=data.get('project_id'))
    except Project.DoesNotExist:
        return Response({"status": "error", "message": "Project does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    if Prototype.objects.filter(project=project, prototype_name=data.get('prototype_name')).exists():
        return Response({"status": "error", "message": "Prototype already exists"}, status=status.HTTP_400_BAD_REQUEST)

    data_str = data.get("data_str", "")
    style_str = data.get("style_str", "")
    prototype = Prototype(
        prototype_id=data.get('prototype_id'),
        prototype_name=data.get('prototype_name'),
        prototype_description=data.get('prototype_description'),
        project=project,
        tag=data.get('tag', 'Normal')
    )
    prototype.save()
    # Save the long string as a txt file in prototype_file
    prototype.prototype_data_file.save(f"{prototype.prototype_id}_data.txt", ContentFile(data_str))
    prototype.prototype_style_file.save(f"{prototype.prototype_id}_style.txt", ContentFile(style_str))
    return Response({"status": "success", "message": "Prototype Created"}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_prototype(request):
    data = request.data

    try:
        prototype = Prototype.objects.get(prototype_id=data.get('prototype_id'))
    except ObjectDoesNotExist:
        return Response({"status": "error", "message": "Prototype does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    # Update fields
    for field in ['prototype_name', 'prototype_description', 'tag']:
        if field in data:
            setattr(prototype, field, data.get(field))

    # Update the long string as a txt file if provided
    data_str = data.get("data_str", None)
    style_str = data.get("style_str", None)
    if data_str is not None:
        prototype.prototype_data_file.save(f"{prototype.prototype_id}_data.txt", ContentFile(data_str))
    if style_str is not None:
        prototype.prototype_style_file.save(f"{prototype.prototype_id}_style.txt", ContentFile(style_str))

    prototype.save()

    return Response({"status": "success", "message": "Prototype Updated"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_prototype(request):
    prototype_id = request.data.get('prototype_id')

    try:
        prototype = Prototype.objects.get(prototype_id=prototype_id)
    except ObjectDoesNotExist:
        return Response({"status": "error", "message": "Prototype does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    # Soft delete by updating the tag to 'Deleted'
    if prototype.tag == 'Deleted':
        prototype.delete()
        return Response({"status": "success", "message": "Prototype Removed Completely"}, status=status.HTTP_200_OK)

    else:
        prototype.tag = 'Deleted'
        prototype.save()
        return Response({"status": "success", "message": "Prototype Removed"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def restore_prototype(request):
    prototype_id = request.data.get('prototype_id')

    try:
        prototype = Prototype.objects.get(prototype_id=prototype_id)
    except ObjectDoesNotExist:
        return Response({"status": "error", "message": "Prototype does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    # Restore the prototype by updating the tag to 'Normal'
    prototype.tag = 'Normal'
    prototype.save()
    return Response({"status": "success", "message": "Prototype Restored"}, status=status.HTTP_200_OK)

# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def get_prototype_file(request):
#     prototype_id = request.GET.get('prototype_id', None)
#
#     if not prototype_id:
#         return Response({"status": "error", "message": "prototype_id parameter is required"},
#                         status=status.HTTP_400_BAD_REQUEST)
#
#     try:
#         prototype = Prototype.objects.get(prototype_id=prototype_id)
#     except Prototype.DoesNotExist:
#         return Response({"status": "error", "message": "Prototype does not exist"}, status=status.HTTP_404_NOT_FOUND)
#
#     if not prototype.prototype_data_file or not prototype.prototype_style_file:
#         return Response({"status": "error", "message": "No prototype file found"}, status=status.HTTP_404_NOT_FOUND)
#
#     try:
#         # with open(prototype.prototype_file.path, 'r') as file:
#         #     long_str = file.read()
#         with open(prototype.prototype_data_file.path, 'r') as file:
#             data_str = file.read()
#         with open(prototype.prototype_style_file.path, 'r') as file:
#             style_str = file.read()
#     except Exception as e:
#         return Response({"status": "error", "message": f"An error occurred while reading the file: {str(e)}"},
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#     return Response({"status": "success", "data": long_str}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_prototypes(request):
    project_id = request.GET.get('project_id', None)
    tag = request.GET.get('tag', None)
    if not project_id:
        return Response({"status": "error", "message": "project_id parameter is required"},
                        status=status.HTTP_400_BAD_REQUEST)
    if tag not in ['Normal', 'Deleted']:
        return Response({"status": "error", "message": "tag parameter is required or invalid"},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        project = Project.objects.get(project_id=project_id)
    except Project.DoesNotExist:
        return Response({"status": "error", "message": "Project does not exist"}, status=status.HTTP_404_NOT_FOUND)

    prototypes = Prototype.objects.filter(project=project, tag=tag)

    serializer = PrototypeSerializer(prototypes, many=True)
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_prototype(request):
    prototype_id = request.GET.get('prototype_id', None)
    if not prototype_id:
        return Response({"status": "error", "message": "prototype_id parameter is required"},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        prototype = Prototype.objects.get(prototype_id=prototype_id)
    except Prototype.DoesNotExist:
        return Response({"status": "error", "message": "Prototype does not exist"}, status=status.HTTP_404_NOT_FOUND)

    response_data = {
        'prototype_id': prototype.prototype_id,
        'prototype_name': prototype.prototype_name,
        'prototype_description': prototype.prototype_description,
        'project_id': prototype.project.project_id if prototype.project else None,
        'tag': prototype.tag,
    }
    return Response({"status": "success", "data": response_data}, status=status.HTTP_200_OK)

