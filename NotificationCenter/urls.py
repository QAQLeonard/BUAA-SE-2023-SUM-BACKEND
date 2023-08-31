from django.urls import path
from NotificationCenter.views import notification_views

urlpatterns = [
    path('get_notification', notification_views.get_notification),
    path('get_user_notifications', notification_views.get_user_notifications),
    path('update_notification', notification_views.update_notification),
]
