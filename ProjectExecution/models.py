from django.db import models
from TeamManagement.models import Team, User, Message


class Project(models.Model):
    TAG_CHOICES = [
        ('Deleted', 'Deleted'),
        ('Normal', 'Normal'),
    ]
    project_id = models.CharField(max_length=40, primary_key=True)
    project_name = models.CharField(max_length=255)
    project_description = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    project_image = models.ImageField(upload_to='resources/project_images/', null=True, blank=True)
    tag = models.CharField(max_length=255, choices=TAG_CHOICES, default='Normal')
    created_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'Projects'

    def __str__(self):
        return self.project_name


class Prototype(models.Model):
    TAG_CHOICES = [
        ('Deleted', 'Deleted'),
        ('Normal', 'Normal'),
    ]

    prototype_id = models.CharField(max_length=60, primary_key=True)
    prototype_name = models.CharField(max_length=255)
    prototype_description = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    prototype_data_file = models.FileField(upload_to='resources/prototype_files/', null=True, blank=True)
    prototype_style_file = models.FileField(upload_to='resources/prototype_files/', null=True, blank=True)
    tag = models.CharField(max_length=255, choices=TAG_CHOICES, default='Normal')
    prototype_preview_file = models.FileField(upload_to='resources/prototype_previews/', null=True, blank=True)

    class Meta:
        db_table = 'Prototypes'

    def __str__(self):
        return self.prototype_name


class Doc(models.Model):
    doc_id = models.CharField(max_length=40, primary_key=True)
    doc_name = models.CharField(max_length=255, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    editable_by_guests = models.BooleanField(default=False, null=True)
    yjs_data = models.BinaryField(null=True)

    class Meta:
        db_table = 'Docs'

    def __str__(self):
        return self.doc_id


class Node(models.Model):
    TYPE_CHOICES = [
        ('Doc', 'Doc'),
        ('Folder', 'Folder'),
    ]
    node_id = models.CharField(max_length=100, primary_key=True)
    node_name = models.CharField(max_length=255)
    node_type = models.CharField(max_length=255, choices=TYPE_CHOICES, default='Doc')
    parent_node = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE, null=True)

    def to_dict(self):
        children = Node.objects.filter(parent_node=self)
        return {
            "id": self.node_id,
            "label": self.node_name,
            "node_type": self.node_type,
            "children": [child.to_dict() for child in children]
        }

