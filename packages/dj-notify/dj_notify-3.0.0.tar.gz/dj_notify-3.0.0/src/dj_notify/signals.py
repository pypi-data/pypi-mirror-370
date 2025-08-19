# dj_notify/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from dj_notify.models import NotificationLog
from dj_notify.notify import send_notification_and_log

@receiver(post_save, sender=NotificationLog)
def auto_send_notification_on_create(sender, instance, created, **kwargs):
    if created:
        send_notification_and_log(instance)
