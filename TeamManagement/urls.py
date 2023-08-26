from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# 创建一个 router 并注册 ViewSet
router = DefaultRouter()
router.register(r'users', user_views.UserCURDViewSet)
router.register(r'teams', team_views.TeamCURDViewSet)
router.register(r'team_members', team_views.TeamMemberCURDViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login', user_views.login),
    path('register', user_views.register),
    path('verification', user_views.get_verification_code),
    path('get_team_members', team_views.get_team_members),
    path('update_user', user_views.update_user),
    path('get_user', user_views.get_user),
    path('create_team', team_views.create_team),
    path('add_team_member', team_views.add_team_member),
    path('get_member_role', team_views.get_user_role_in_team),
]
