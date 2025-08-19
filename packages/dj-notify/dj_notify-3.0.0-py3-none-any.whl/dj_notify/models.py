from django.db import models
from django.conf import settings
from dj_notify.utils import send_email, send_whatsapp


class NotificationLog(models.Model):
    class NotificationType(models.TextChoices):
        EMAIL = 'email', 'Email'
        WHATSAPP = 'whatsapp', 'WhatsApp'

    class NotificationStatus(models.TextChoices):
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'

    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    sent_from = models.CharField(max_length=255)
    sent_to = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.SENT)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} from {self.sent_from} to {self.sent_to}"


    



