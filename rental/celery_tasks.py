from celery import shared_task
from .models import Orders


@shared_task
def set_total_price(order_id):
    order = Orders.objects.get(id=order_id)
    total_price = (order.rent_finish - order.rent_start).seconds * order.bicycle.price
    order.total_price = total_price
    order.save()
    return order.total_price
