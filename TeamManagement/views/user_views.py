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
from shared.utils.TeamManage.users import *
from shared.utils.email import send_email


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


@api_view(['PUT'])
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


@api_view(['POST'])
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


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user(request):
    username = request.GET.get('username')
    email = request.GET.get('email')

    query = Q()
    if username:
        query |= Q(username=username)
    if email:
        query |= Q(email=email)

    if not query:
        return JsonResponse({"status": "error", "message": "At least one parameter is required"},
                            status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.get(query)

    if not user:
        return JsonResponse({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user)
    return JsonResponse({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def set_user_avatar(request):
    if request.method == 'POST':
        image = request.FILES['avatar']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        url = fs.url(filename)

        user = request.user
        user.avatar = url  # assuming `avatar` is a field in the `Profile` model
        user.save()

        return JsonResponse({'status': 'success', 'message': 'Avatar updated'})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
