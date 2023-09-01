from rest_framework import serializers
from .models import Project, Prototype, Node


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('project_id', 'project_name', 'project_description', 'team', 'project_image', 'tag')


class PrototypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prototype
        fields = ('prototype_id', 'prototype_name', 'prototype_description')


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ['node_id', 'node_name', 'node_type', 'parent_node', 'doc']
