from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from celery import shared_task
from django_users.tokens import account_activation_token
from .models import CustomUser


@shared_task
def send_activation_email(template, domain, user_pk):
    try:
        user = CustomUser.objects.get(pk=user_pk)
        mail_subject = 'Activate your account!'
        message = render_to_string(template, {
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user)
        })
        email = EmailMessage(mail_subject, message, to=[user.email])
        email.send()
    except Exception as err:
        print(err)
    return None
