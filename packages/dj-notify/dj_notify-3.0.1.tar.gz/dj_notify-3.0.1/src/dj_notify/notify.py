# dj_notify/notify.py
from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client
from .models import NotificationLog

def send_notification_and_log(instance):
    recipient = instance.sent_to
    message = instance.message

    if "@" in recipient:
        sender = getattr(settings, 'DJ_NOTIFY_DEFAULT_EMAIL_FROM', settings.DEFAULT_FROM_EMAIL)
        subject = "Notification"
        try:
            send_mail(subject, message, sender, [recipient])
            instance.notification_type = 'email'
            instance.sent_from = sender
            instance.status = 'sent'
        except Exception as e:
            instance.notification_type = 'email'
            instance.sent_from = sender
            instance.status = 'failed'
            instance.message += f"\nError: {str(e)}"
    else:
        sender = settings.TWILIO_WHATSAPP_NUMBER
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        try:
            client.messages.create(
                body=message,
                from_=f"whatsapp:{sender}",
                to=f"whatsapp:{recipient}",
            )
            instance.notification_type = 'whatsapp'
            instance.sent_from = sender
            instance.status = 'sent'
        except Exception as e:
            instance.notification_type = 'whatsapp'
            instance.sent_from = sender
            instance.status = 'failed'
            instance.message += f"\nError: {str(e)}"

    instance.save(update_fields=['notification_type', 'sent_from', 'status', 'message'])
