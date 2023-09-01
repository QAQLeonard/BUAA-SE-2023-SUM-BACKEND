from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from ProjectExecution.models import Doc, Node, Project, Prototype


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_all_nodes(request):
    root_nodes = Node.objects.filter(parent_node__isnull=True)
    tree = [root.to_dict() for root in root_nodes]
    return JsonResponse({"data": tree}, safe=False)


@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_children_nodes(request):
    try:
        node_id = request.GET.get('node_id')
        parent_node = Node.objects.get(node_id=node_id)
        children = Node.objects.filter(parent_node=parent_node)
        tree = [child.to_dict() for child in children]
        return JsonResponse({"data": tree}, safe=False)
    except Node.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Node not found"})


@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_node(request):
    try:
        data = request.data
        node = Node.objects.create(
            node_id=data['node_id'],
            node_name=data['node_name'],
            node_type=data['node_type'],
            parent_node=Node.objects.get(pk=data['parent_id']) if data.get('parent_id') else None,
            # Assume Doc object is created and its instance is available
        )
        node.save()
        return JsonResponse({"status": "success", "message": f"Node {node.node_id} created"},
                            status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
        return JsonResponse({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_node(request):
    try:
        node_id = request.data.get('node_id')
        node = Node.objects.get(node_id=node_id)
        data = request.data
        node.node_name = data.get('node_name', node.node_name)
        # Update doc content if applicable
        node.save()
        return JsonResponse({"status": "success", "message": f"Node {node.node_id} updated"})
    except Node.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Node not found"})


@csrf_exempt
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_node(request):
    try:
        node_id = request.data.get('node_id')
        node = Node.objects.get(node_id=node_id)
        node.delete()
        return JsonResponse({"status": "success", "message": f"Node {node_id} deleted"})
    except Node.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Node not found"})


