from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


@shared_task
def send_order_email(template, user, order):
    try:

        mail_subject = 'Order placed!'
        message = render_to_string(template, {
            'customer': user.customer,
            'order': order
        })
        email = EmailMessage(mail_subject, message, to=[user.email])
        email.send()
    except Exception as err:
        print(err)
    return None
