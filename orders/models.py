from django.contrib.auth.models import User
from django.db import models

from core.models import DatedModel, CreatedByModel
from inventory.models import Medicine, Store, Cluster
from orders.constants import OrderStatusTypes


class Rider(DatedModel, CreatedByModel):
    user = models.OneToOneField(
        User, on_delete=models.PROTECT,
        related_name="user_rider")
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=32)
    cluster = models.ForeignKey(Cluster, on_delete=models.PROTECT)
    mobile_number = models.CharField(max_length=32)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class Order(DatedModel, CreatedByModel):
    code = models.CharField(max_length=32)
    location = models.CharField(max_length=128)
    contact_number = models.CharField(max_length=32)
    status = models.CharField(
        max_length=64,
        choices=OrderStatusTypes.choices,
        default=OrderStatusTypes.CREATED)
    cluster = models.ForeignKey(
        Cluster, on_delete=models.PROTECT)

    def __str__(self):
        return self.code


class OrderItem(DatedModel):
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    store = models.ForeignKey(
        Store, on_delete=models.PROTECT)
    value = models.PositiveIntegerField()

    def __str__(self):
        return f"[{self.quantity}] - {self.medicine.name}"



class Bucket(DatedModel):
    rider = models.ForeignKey(Rider, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.id}] - {self.rider.name}"


class BucketItem(DatedModel):
    bucket = models.ForeignKey(Bucket, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    is_delivered = models.BooleanField(default=False)
    order_number = models.PositiveIntegerField()

    def __str__(self):
        return f"[{self.order_number}] - {self.order.code}"


class Customer(DatedModel):
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, related_name="customer")
    userEID = models.CharField(max_length=128)

    def __str__(self):
        return f"[{self.userEID}] - {self.user.username}"
