from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from django_users.tokens import account_activation_token


def send_email(template,domain,user, to_email):
    mail_subject = 'Activate your account!'
    message = render_to_string(template, {
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user)
    })
    to_email = to_email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()