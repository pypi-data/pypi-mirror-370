# dj_notify/admin.py
from django.contrib import admin
from dj_notify.models import NotificationLog
from dj_notify.notify import send_notification_and_log

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'sent_from', 'sent_to', 'status', 'sent_at')