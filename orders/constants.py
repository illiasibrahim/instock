from django.db import models


class OrderStatusTypes(models.TextChoices):
    CREATED = 'created', 'Created'
    PACKED = 'packed', 'Packed'
    PICKED = 'picked', 'picked'
    DELIVERED = 'delivered', 'Delivered'
