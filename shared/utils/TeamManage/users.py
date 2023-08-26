from TeamManagement.models import User


def get_user_by_email(email):
    users = User.objects.filter(email=email)
    if users.exists():
        return users.first()
    return None


def get_user_by_username(username: str):
    users = User.objects.filter(username=username)
    if users.exists():
        return users.first()
    return None
