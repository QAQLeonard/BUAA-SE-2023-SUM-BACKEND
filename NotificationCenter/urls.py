from django.urls import path
from NotificationCenter.views import notification_views

urlpatterns = [
    path('get_notification', notification_views.get_notification),
    path('get_user_notifications', notification_views.get_user_notifications),
    path('update_notification', notification_views.update_notification),
    path('delete_notification', notification_views.delete_notification),
    path('delete_read_notifications', notification_views.delete_read_notifications),
    path('read_all_notifications', notification_views.read_all_notifications),
    path('create_doc_notification', notification_views.create_doc_notification),
]
