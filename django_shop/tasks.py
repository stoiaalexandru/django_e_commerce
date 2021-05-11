from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django_shop.models import Customer, Order



@shared_task
def send_order_email(template, order_pk, ):
    try:
        order = Order.objects.filter(pk=order_pk).get()
        user = order.customer.user
        customer = order.customer

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

    file_content = "Order ID,Order Date,Product,Key\n"
    for item in items:
        for key in item.keys.all():
            file_content += "{},{},{},{}\n".format(order.id, order.ordered, item.product_name, key.key)

    mail_subject = 'History for order {} from {}'.format(order.id, order.ordered)
    message = render_to_string(template, {
        'customer': order.customer,
        'order': order
    })

    email = EmailMultiAlternatives(mail_subject, message, "no-reply@e-commerce.ro", to=[order.customer.user.email])
    email.attach_alternative(message, "text/html")
    email.attach('order_ID{}_{}.csv'.format(order.pk, order.ordered), file_content, 'text/csv')
    email.send()


@shared_task
def send_order_history_all_email(template, customer_pk):
    customer = Customer.objects.filter(pk=customer_pk).get()

    file_content = "Order ID,Order Date,Product,Key\n"
    for order in customer.orders.all():
        for item in order.history_items.all():
            for key in item.keys.all():
                file_content += "{},{},{},{}\n".format(order.id, order.ordered, item.product_name, key.key)

    mail_subject = 'History for all orders'
    message = render_to_string(template, {
        'customer': customer,
        'order_list': customer.orders.all()
    })

    email = EmailMultiAlternatives(mail_subject, message, "no-reply@e-commerce.ro", to=[customer.user.email])
    email.attach_alternative(message, "text/html")
    email.attach('order_history.csv', file_content, 'text/csv')
    email.send()
