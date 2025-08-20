"""Main source file."""

from typing import Dict, List, Optional

from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.mail.backends.base import BaseEmailBackend
from django.http import HttpRequest
from django.template.loader import get_template
from nmdmail.api import EmailContent


def send_mail(
    subject: str,
    message: str,
    from_email: str,
    recipient_list: List[str],
    context: Optional[Dict] = None,
    request: Optional[HttpRequest] = None,
    fail_silently: bool = False,
    css: Optional[str] = None,
    image_root: str = ".",
    auth_user: Optional[str] = None,
    auth_password: Optional[str] = None,
    connection: Optional[BaseEmailBackend] = None,
    reply_to: Optional[List[str]] = None,
) -> int:
    """Drop in replacement for django.core.email.send_mail."""
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    if context is not None:
        message = get_template(message).render(context, request)
    content = EmailContent(message, css=css, image_root=image_root)
    mail = EmailMultiAlternatives(
        subject,
        content.text,
        from_email,
        recipient_list,
        connection=connection,
        reply_to=reply_to,
    )
    for filename, data in content.inline_images:
        mail.attach(filename, data)
    mail.attach_alternative(content.html, "text/html")

    return mail.send()
