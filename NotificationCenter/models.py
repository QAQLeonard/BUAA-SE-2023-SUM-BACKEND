from django.db import models

# Create your models here.
from ProjectExecution.models import Doc
from TeamManagement.models import User, Message


class Notification(models.Model):
    TYPE_CHOICES = (
        ('group_chat', 'Group Chat Mention'),
        ('document', 'Document Mention'),
        ('system', 'System Notification')
    )
    notification_id = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=255)
    # 对于文档 "@"
    doc = models.ForeignKey(Doc, null=True, on_delete=models.CASCADE)
    # 对于群聊 "@"
    message = models.ForeignKey(Message, null=True, on_delete=models.CASCADE)