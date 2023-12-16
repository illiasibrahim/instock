from django.contrib.auth.models import User
from django.db import models

from core.models import DatedModel, CreatedByModel
from inventory.models import Medicine, Store, Cluster


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
    rider = models.ForeignKey(
        Rider, on_delete=models.PROTECT,
        null=True, blank=True)

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
