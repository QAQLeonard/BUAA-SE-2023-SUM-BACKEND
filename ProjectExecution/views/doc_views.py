import html2text
import pdfkit
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from docx import Document
from rest_framework import status
from rest_framework.decorators import api_view
from xhtml2pdf import pisa
from ProjectExecution.models import Doc
from ProjectExecution.views.decorators import require_doc, require_project
from TeamManagement.models import TeamMember, User


# 创建文档
@csrf_exempt
@api_view(['POST'])
@require_project
def create_doc(request):
    doc_id = request.data.get('doc_id')
    project = request.project_object
    doc_name = request.data.get('doc_name')
    model_id = request.data.get('model_id')
    # 校验参数
    if not doc_id or not doc_name:
        print("Missing required fields")
        return JsonResponse({"status": "error", "message": "Missing required fields"},
                            status=status.HTTP_400_BAD_REQUEST)
    yjs_data = None
    if model_id:
        try:
            print(model_id)
            model_doc = Doc.objects.get(doc_id=model_id)
            yjs_data = model_doc.yjs_data  # 从模型文档中获取yjs_data
        except Doc.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Model document not found"},
                                status=status.HTTP_400_BAD_REQUEST)

    if Doc.objects.filter(doc_id=doc_id).exists():
        doc = Doc.objects.get(doc_id=doc_id)
        doc.doc_name = doc_name
        doc.project = project
        doc.yjs_data = yjs_data
        doc.save()
    else:
        doc = Doc(doc_id=doc_id, project=project, doc_name=doc_name, yjs_data=yjs_data)
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
@require_doc
def update_doc(request):
    doc_name = request.data.get('doc_name')
    doc = request.doc_object
    if doc_name:
        doc.doc_name = doc_name
    else:
        doc.editable_by_guests = not doc.editable_by_guests
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


@csrf_exempt
@api_view(['POST'])
@require_doc
def convert_format(request):
    file_format = request.data.get('file_format')
    doc = request.doc_object
    doc_id = doc.doc_id
    html = request.data.get('html')
    title = "<h1>" + Doc.objects.get(doc_id=doc_id).doc_name + "</h1>"
    html = title + html
    if not html:
        return JsonResponse({"status": "error", "message": "Missing required fields"},
                            status=status.HTTP_400_BAD_REQUEST)
    file_path = f"resources/trans_doc/{doc_id}.{file_format}"

    if file_format == 'pdf':
        try:
            options = {
                'encoding': 'UTF-8',
                'custom-header': [
                    ('Content-Type', 'text/html; charset=UTF-8')
                ],
                '--custom-header': f"<style>@font-face {{ font-family: 'MyFont'; src: url('/usr/share/fonts/truetype/myfonts/Microsoft YaHei UI Bold.ttf'); }} body {{ font-family: 'MyFont'; }}</style>"
            }
            pdfkit.from_string(html, file_path, options=options)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"PDF generation error: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif file_format == 'docx':
        doc = Document()
        doc.add_paragraph(html)
        doc.save(file_path)

    elif file_format == 'md':
        converter = html2text.HTML2Text()
        markdown_text = converter.handle(html)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)

    else:
        return JsonResponse({"status": "error", "message": "Unsupported file format"},
                            status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"status": "success", "message": "File converted", "file": file_path},)


@csrf_exempt
def document_data(request, doc_id):
    if request.method == 'GET':
        try:
            doc = Doc.objects.get(doc_id=doc_id)
            return JsonResponse({"data": doc.yjs_data})
        except Doc.DoesNotExist:
            return HttpResponseBadRequest('Document not found')

    elif request.method == 'POST':
        try:
            yjs_data = request.body
            doc, created = Doc.objects.get_or_create(
                doc_id=doc_id,
                defaults={'yjs_data': yjs_data}
            )
            if not created:
                doc.yjs_data = yjs_data
                doc.save()
            return JsonResponse({"message": "Document saved successfully"})
        except Exception as e:
            print(e)
            return HttpResponseBadRequest(str(e))
