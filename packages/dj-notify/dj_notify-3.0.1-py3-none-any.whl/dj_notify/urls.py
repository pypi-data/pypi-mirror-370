from django.urls import path
from dj_notify.views import whatsapp_webhook, email_reply_webhook

urlpatterns = [
    path('webhook/whatsapp/', whatsapp_webhook, name='whatsapp_webhook'),
    path("webhook/email-reply/", email_reply_webhook, name='email_webhook'),
]
