from django.contrib.auth.models import AbstractUser
from django.db import models

# User model, extending Django's AbstractUser
from shared.utils.datetime import get_expiry_time


class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True, primary_key=True)
    real_name = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    has_completed_tutorial = models.BooleanField(default=False)

    class Meta:
        db_table = 'Users'

    def __str__(self):
        return self.username


class Team(models.Model):
    team_id = models.CharField(max_length=40, primary_key=True)
    team_name = models.CharField(max_length=255)
    team_description = models.CharField(max_length=255)

    class Meta:
        db_table = 'Teams'

    def __str__(self):
        return self.team_name


class TeamMember(models.Model):
    ROLE_TYPE_CHOICES = [
        ('Creator', 'Creator'),
        ('Admin', 'Admin'),
        ('Member', 'Member'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=255,
        choices=ROLE_TYPE_CHOICES,
        default='Member',
    )

    class Meta:
        db_table = 'TeamMembers'
        unique_together = ['team', 'user']  # 确保每个组合的(team, user)是唯一的

    def __str__(self):
        return f"{self.team} - {self.user} ({self.get_role_display()})"


class ChatGroup(models.Model):
    GROUP_TYPE_CHOICES = [
        ('Team', 'Team'),
        ('Public', 'Public'),
        ('Private', 'Private'),
    ]
    group_id = models.CharField(max_length=60, primary_key=True)
    group_name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    group_type = models.CharField(max_length=255, choices=GROUP_TYPE_CHOICES, default='Team')

    class Meta:
        db_table = 'ChatGroups'

    def __str__(self):
        return self.group_name


class GroupMember(models.Model):
    ROLE_TYPE_CHOICES = [
        ('Creator', 'Creator'),
        ('Admin', 'Admin'),
        ('Member', 'Member'),
    ]
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=255, default='Member')

    class Meta:
        db_table = 'GroupMembers'

    def __str__(self):
        return str(self.group)


class Message(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('Text', 'Text'),
        ('Image', 'Image'),
        ('File', 'File'),
    ]

    message_id = models.CharField(max_length=60, primary_key=True)
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    message_type = models.CharField(max_length=255, choices=MESSAGE_TYPE_CHOICES, default='Text')

    class Meta:
        db_table = 'Messages'

    def __str__(self):
        return self.message_id


class VerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_expiry_time)

    def __str__(self):
        return self.email



