from django.db import models

# Create your models here.
from TeamManagement.models import *


class Project(models.Model):
    project_id = models.CharField(max_length=20, primary_key=True)
    project_name = models.CharField(max_length=255)
    project_description = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    project_image = models.ImageField(upload_to='project_images/', null=True, blank=True)

    class Meta:
        db_table = 'Projects'

    def __str__(self):
        return self.project_name
