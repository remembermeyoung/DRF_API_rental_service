from django.db.models.signals import post_save
from django.dispatch import receiver
from .celery_tasks import set_total_price
from rental.models import Orders


@receiver(post_save, sender=Orders)
def handler(instance, **kwargs):
    if instance.rent_finish and not instance.total_price:
        set_total_price.delay(instance.id)