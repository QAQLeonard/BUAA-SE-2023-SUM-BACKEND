from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, status
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
import random
import json
from TeamManagement.serializers import *
from shared.decorators import require_user
from shared.utils.TeamManage.users import *
from shared.utils.email import send_email
import shutil
import os


class UserCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['POST'])
@csrf_exempt
def login(request):
    data = json.loads(request.body.decode('utf-8'))

    username = data.get('username')
    password = data.get('password')

    try:
        user = User.objects.get(username=username)
        if check_password(password, user.password):
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({"status": "success", "token": str(token.key)}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({"status": "wrong password"}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return JsonResponse({"status": "user does not exist"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@csrf_exempt
def register(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username')
    password = data.get('password')
    real_name = data.get('real_name')
    email = data.get('email')
    code = data.get('code')

    if not password or not email or not code or not username or not real_name:
        return JsonResponse({"status": "error", "message": "ALL messages are required"},
                            status=status.HTTP_400_BAD_REQUEST)

    verification_code = VerificationCode.objects.filter(email=email).order_by('-created_at').first()

    if not verification_code or verification_code.code != code:
        return JsonResponse({"status": "error", "message": "ERROR CODE"}, status=status.HTTP_401_UNAUTHORIZED)

    if verification_code.expires_at < timezone.now():
        print(verification_code.expires_at)
        print(timezone.now())
        return JsonResponse({"status": "error", "message": "Verification code expired"},
                            status=status.HTTP_401_UNAUTHORIZED)

    if get_user_by_email(email) or get_user_by_username(username):
        return JsonResponse({"status": "error", "message": "User already exists"}, status=status.HTTP_409_CONFLICT)

    hashed_password = make_password(password)
    verification_code.delete()
    new_user = User(password=hashed_password, username=username, real_name=real_name, email=email)
    new_user.save()

    default_avatar_path = '/avatars/default_avatar.png'
    with open(default_avatar_path, 'rb') as f:
        avatar_content = f.read()
    new_filename = f"{username}_avatar.png"
    new_file = ContentFile(avatar_content)
    new_file.name = new_filename
    new_user.avatar.save(new_filename, new_file, save=True)


    return JsonResponse({"status": "success", "message": "User successfully registered"},
                        status=status.HTTP_201_CREATED)


@api_view(['POST'])
@csrf_exempt
def get_verification_code(request):
    email = request.GET.get('email')

    if not email:
        return JsonResponse({"status": "error", "message": "email is required"}, status=status.HTTP_400_BAD_REQUEST)

    code = str(random.randint(1000, 9999))

    # 保存验证码
    VerificationCode.objects.create(email=email, code=code)
    print(timezone.now())
    # 在这里添加发送邮件的代码
    send_email(email, code)

    return JsonResponse({"status": "success", "message": "Verification code sent"}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_user(request):
    data = request.data  # 获取前端传入的JSON数据

    # 获取通过Token验证的当前用户
    current_user = request.user

    # 检查username是否与当前Token用户匹配
    if data.get("username") != current_user.username:
        return JsonResponse({"status": "error", "message": "You can only update your own profile"},
                            status=status.HTTP_401_UNAUTHORIZED)

    verification_code = VerificationCode.objects.filter(email=current_user.email).order_by('-created_at').first()

    if not verification_code or verification_code.code != data.get('code'):
        return JsonResponse({"status": "error", "message": "ERROR CODE"}, status=status.HTTP_401_UNAUTHORIZED)

    if verification_code.expires_at < timezone.now():
        print(verification_code.expires_at)
        print(timezone.now())
        return JsonResponse({"status": "error", "message": "Verification code expired"},
                            status=status.HTTP_401_UNAUTHORIZED)

    # 在这里进行实际的更新操作
    try:
        # 更新密码
        if not check_password(data.get('password'), current_user.password):
            current_user.set_password(data.get('password'))
        # 更新真实姓名
        if data.get('real_name') != current_user.real_name:
            current_user.real_name = data.get('real_name')
        # 更新邮箱
        if data.get('email') != current_user.email:
            if get_user_by_email(data.get('email')):
                return JsonResponse({"status": "error", "message": "Email already used"})
            current_user.email = data.get('email')
        # 保存更改
        current_user.save()
        return JsonResponse({"status": "success", "message": "Profile updated successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_user
def update_user_tutorial(request):
    user = request.user_object
    has_completed_tutorial = request.GET.get('has_completed_tutorial')
    if not has_completed_tutorial:
        return JsonResponse({"status": "error", "message": "has_completed_tutorial are required"},
                            status=status.HTTP_400_BAD_REQUEST)
    user.has_completed_tutorial = has_completed_tutorial
    user.save()
    return JsonResponse({"status": "success", "message": "Tutorial status updated successfully"},
                        status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_user
def get_user(request):
    user = request.user_object
    serializer = UserSerializer(user)
    return JsonResponse({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def set_user_avatar(request):
    try:
        # 从请求中获取文件
        avatar = request.FILES.get('avatar', None)
        if not avatar:
            return JsonResponse({"status": "error", "message": "No avatar file provided"},
                                status=status.HTTP_400_BAD_REQUEST)
        # 获取用户
        user = User.objects.get(username=request.user.username)
        # 删除旧的头像文件，如果存在的话
        if user.avatar:
            user.avatar.delete(save=False)
        # 创建新的头像文件名
        new_filename = f"{user.username}_avatar.png"
        # 读取和保存新文件
        new_file = ContentFile(avatar.read())
        new_file.name = new_filename
        # 保存新的头像
        user.avatar.save(new_filename, new_file, save=True)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({"status": "success", "message": "Avatar updated successfully"}, status=status.HTTP_200_OK)
