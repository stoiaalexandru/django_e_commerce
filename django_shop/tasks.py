from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from django_shop.models import Customer, Order
from django_users.models import CustomUser


@shared_task
def send_order_email(template, user_pk, order_pk, customer_pk):
    try:
        user = CustomUser.objects.filter(pk=user_pk).get()
        order = CustomUser.objects.filter(pk=order_pk).get()
        customer = CustomUser.objects.filter(pk=customer_pk).get()
        mail_subject = 'Order placed!'
        message = render_to_string(template, {
            'customer': customer,
            'order': order
        })

        email = EmailMessage(mail_subject, message, to=[user.email])
        email.send()
    except Exception as err:
        print(err)
    return None
