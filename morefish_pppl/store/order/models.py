from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import CoreModel


# Create your models here.
class OrderBillingAddress(CoreModel):
    district = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=150, blank=True, null=True)
    address_line_1 = models.TextField(blank=True, null=True)
    address_line_2 = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.city


class OrderShippingAddress(CoreModel):
    district = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=150, blank=True, null=True)
    address_line_1 = models.TextField(blank=True, null=True)
    address_line_2 = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.city


class Order(CoreModel):
    STATUS_PENDING = 1
    STATUS_PROCESSING = 2
    STATUS_COMPLETED = 3
    STATUS_CANCELLED = 4

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(
        "users.User", blank=True, null=True, on_delete=models.DO_NOTHING
    )
    order_status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    shipping_address = models.OneToOneField(
        "order.OrderShippingAddress", blank=True, null=True, on_delete=models.DO_NOTHING
    )
    billing_address = models.OneToOneField(
        "order.OrderBillingAddress", blank=True, null=True, on_delete=models.DO_NOTHING
    )

    def __str__(self) -> str:
        return self.user.first_name


class OrderItem(CoreModel):
    order = models.ForeignKey(
        "order.Order", blank=True, null=True, on_delete=models.DO_NOTHING
    )
    order_item = models.ForeignKey(
        "product.Product", blank=True, null=True, on_delete=models.DO_NOTHING
    )
    order_price = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.order_item.name
