from TeamManagement.models import *
from TeamManagement.serializers import *


def get_users_from_uid_list(uid_list, serializer):
    user_list = []
    for uid in uid_list:
        users = User.objects.filter(uid=uid)
        if not users.exists():
            continue
        user_list.append(serializer(users.first()).data)
    return user_list


def get_users_from_user_list(user_list, serializer):
    users = []
    for user in user_list:
        users.append(serializer(user).data)
    return users
