from celery import shared_task
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

from django_shop.models import Customer, Order
from django_users.models import CustomUser
import csv


@shared_task
def send_order_email(template, user_pk, order_pk, customer_pk):
    try:
        user = CustomUser.objects.filter(pk=user_pk).get()
        order = Order.objects.filter(pk=order_pk).get()
        customer = Customer.objects.filter(pk=customer_pk).get()
        mail_subject = 'Order placed!'
        message = render_to_string(template, {
            'customer': customer,
            'order': order
        })

        email = EmailMultiAlternatives(mail_subject, message, "no-reply@e-commerce.ro", to=[user.email])
        email.attach_alternative(message, "text/html")
        email.send()

    except Exception as err:
        print(err)
    return None


@shared_task
def send_order_history_single_email(template, order_pk):
    order = Order.objects.filter(pk=order_pk).get()
    items = order.history_items.all()

    with open('order_ID{}_{}.csv'.format(order.pk, order.ordered), mode='w') as order_file:
        order_writer = csv.writer(order_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for item in items:
            for key in item.keys:
                order_writer.writerow([order.id, order.ordered, item.product_name, key.key])

    mail_subject = 'History for order {} from {}'.format(order.id, order.ordered)
    message = render_to_string(template, {
        'customer': order.customer,
        'order': order
    })

    email = EmailMultiAlternatives(mail_subject, message, "no-reply@e-commerce.ro", to=[order.customer.user.email])
    email.attach_alternative(message, "text/html")
    email.attach(order_file.name, order_file.read(), 'text/csv')
    email.send()
