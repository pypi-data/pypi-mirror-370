# notify_service/main.py
from .senders import _send_email_internal, _send_whatsapp_internal

def notify(channel: str, recipient: str, message: str, subject: str = None):
    """
    The main public function to send a notification.

    :param channel: 'email' or 'whatsapp'.
    :param recipient: The email address or full E.164 phone number.
    :param message: The body of the message.
    :param subject: The subject line (required for email).
    """
    if channel == 'email':
        if not subject:
            raise ValueError("Parameter 'subject' is required for the email channel.")
        _send_email_internal(subject=subject, message=message, recipient_email=recipient)
    elif channel == 'whatsapp':
        _send_whatsapp_internal(message=message, recipient_number=recipient)
    else:
        raise ValueError(f"Unknown channel: '{channel}'. Use 'email' or 'whatsapp'.")