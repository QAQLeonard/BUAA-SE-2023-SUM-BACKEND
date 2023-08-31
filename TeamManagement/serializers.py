# TeamManage/serializers.py

from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'real_name', 'has_completed_tutorial')


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class TeamMemberUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # 嵌套使用 UserSerializer
    role = serializers.CharField()  # 显式声明，以便将其包括在序列化输出中

    class Meta:
        model = TeamMember
        fields = ('user', 'role')  # 返回 'user' 和 'role'


class TeamMemberTeamSerializer(serializers.ModelSerializer):
    team = TeamSerializer()
    role = serializers.CharField()

    class Meta:
        model = TeamMember
        fields = ('team', 'role')

