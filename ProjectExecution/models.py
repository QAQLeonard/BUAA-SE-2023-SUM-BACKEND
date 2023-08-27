from django.db import models

# Create your models here.
from TeamManagement.models import *


class Project(models.Model):
    project_id = models.CharField(max_length=40, primary_key=True)
    project_name = models.CharField(max_length=255)
    project_description = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    project_image = models.ImageField(upload_to='project_images/', null=True, blank=True)

    class Meta:
        db_table = 'Projects'

    def __str__(self):
        return self.project_name


class Prototype(models.Model):
    TAG_CHOICES = [
        ('Deleted', 'Deleted'),
        ('Normal', 'Normal'),
    ]

    prototype_id = models.CharField(max_length=40, primary_key=True)
    prototype_name = models.CharField(max_length=255)
    prototype_description = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    prototype_file = models.FileField(upload_to='prototype_files/', null=True, blank=True)
    tag = models.CharField(max_length=255, choices=TAG_CHOICES, default='Normal')

    class Meta:
        db_table = 'Prototypes'

    def __str__(self):
        return self.prototype_name
