from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from dj_notify.models import NotificationLog


@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'POST':
        from_number = request.POST.get("From")
        body = request.POST.get("Body")

        # Save to DB
        NotificationLog.objects.create(
            sent_to=from_number.replace("whatsapp:", ""),
            message=body,
            notification_type="whatsapp",
            status="sent"
        )
        response_message = f"Thanks, we received: {body}"
        return HttpResponse(f'<Response><Message>{response_message}</Message></Response>', content_type='text/xml')

    return HttpResponse('Method Not Allowed', status=405)


@csrf_exempt
def email_reply_webhook(request):
    if request.method == "POST":
        sender = request.POST.get("sender")
        subject = request.POST.get("subject")
        body_plain = request.POST.get("body-plain")

        NotificationLog.objects.create(
            sent_to=sender,
            message=body_plain,
            notification_type="email",
            status="sent"
        )
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "invalid"}, status=400)