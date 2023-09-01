from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from portalocker import Lock
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ProjectExecution.models import Project, Prototype
from ProjectExecution.serializers import PrototypeSerializer
from ProjectExecution.views.decorators import require_prototype, require_project


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
@require_prototype
def update_prototype(request):
    data = request.data
    prototype = request.prototype_object
    # Update fields
    for field in ['prototype_name', 'prototype_description', 'tag']:
        if field in data:
            setattr(prototype, field, data.get(field))

    # Update the long string as a txt file if provided
    data_str = data.get("data_str", None)
    style_str = data.get("style_str", None)
    if data_str is not None:
        with Lock(prototype.prototype_data_file.path, 'w') as file:
            # Save the long string as a txt file in prototype_file
            prototype.prototype_data_file.delete(save=False)
            new_data_file = ContentFile(data_str)
            new_data_file.name = f"{prototype.prototype_id}_data.txt"
            prototype.prototype_data_file.save(new_data_file.name, new_data_file)
            prototype.save()
    if style_str is not None:
        with Lock(prototype.prototype_style_file.path, 'w') as file:
            prototype.prototype_style_file.delete(save=False)
            new_style_file = ContentFile(style_str)
            new_style_file.name = f"{prototype.prototype_id}_style.txt"
            prototype.prototype_style_file.save(new_style_file.name, new_style_file)
            prototype.save()
    prototype.save()
    return Response({"status": "success", "message": "Prototype Updated"}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_prototype
def delete_prototype(request):
    prototype = request.prototype_object
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
@require_prototype
def restore_prototype(request):
    prototype = request.prototype_object
    if prototype.tag != 'Deleted':
        return Response({"status": "error", "message": "Prototype is not deleted"}, status=status.HTTP_400_BAD_REQUEST)
    # Restore the prototype by updating the tag to 'Normal'
    prototype.tag = 'Normal'
    prototype.save()
    return Response({"status": "success", "message": "Prototype Restored"}, status=status.HTTP_200_OK)


# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# @require_prototype
# def get_prototype_file(request):
#     prototype = request.prototype_object
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
@require_project
def get_project_prototypes(request):
    project = request.project_object
    tag = request.GET.get('tag', None)
    if tag not in ['Normal', 'Deleted']:
        return Response({"status": "error", "message": "tag parameter is required or invalid"},
                        status=status.HTTP_400_BAD_REQUEST)

    prototypes = Prototype.objects.filter(project=project, tag=tag)

    serializer = PrototypeSerializer(prototypes, many=True)
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_prototype
def get_prototype(request):
    prototype = request.prototype_object
    response_data = {
        'prototype_id': prototype.prototype_id,
        'prototype_name': prototype.prototype_name,
        'prototype_description': prototype.prototype_description,
        'project_id': prototype.project.project_id if prototype.project else None,
        'tag': prototype.tag,
    }
    return Response({"status": "success", "data": response_data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_prototype
def save_prototype_preview(request):
    prototype = request.prototype_object
    data = request.data.get('data_str', None)
    if not data:
        return Response({"status": "error", "message": "data_str is required"}, status=status.HTTP_400_BAD_REQUEST)
    data_filename = f"{prototype.prototype_id}_preview_data.txt"
    file_path = f"resources/prototype_previews/{data_filename}"
    # Save the long string as a txt file in prototype_file
    if prototype.prototype_preview_file:
        prototype.prototype_preview_file.delete(save=False)
    data_file = ContentFile(data)
    data_file.name = data_filename
    prototype.prototype_preview_file.save(data_filename, data_file)

    return Response({"status": "success", "message": "Prototype Preview Saved"}, status=status.HTTP_200_OK)
