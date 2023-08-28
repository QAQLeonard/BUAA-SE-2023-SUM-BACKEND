from rest_framework import serializers
from .models import Project, Prototype


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('project_id', 'project_name', 'project_description', 'team', 'project_image', 'tag')


class PrototypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prototype
        fields = ('prototype_id', 'prototype_name', 'prototype_description')
