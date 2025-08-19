import string
import random
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings

def generate_unique_order_reference():
    code_length = 20
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=code_length))

    Order = apps.get_model(settings.PAYMENT_ORDER_MODEL)

    while Order.objects.filter(order_reference=code).exists():
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=code_length))

    return code

@receiver(pre_save)
def set_order_reference(sender, instance, **kwargs):
    # Only apply to the user-defined Order model
    OrderModel = apps.get_model(settings.PAYMENT_ORDER_MODEL)
    if sender == OrderModel and not instance.order_reference:
        instance.order_reference = generate_unique_order_reference()
