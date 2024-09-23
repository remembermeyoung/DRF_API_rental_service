from celery import shared_task


@shared_task()
def set_total_price(current_order):
    total_price = (current_order.rent_finish - current_order.rent_start).seconds * current_order.bicycle.price
    current_order.total_price = total_price
    current_order.save()
    return current_order.total_price
