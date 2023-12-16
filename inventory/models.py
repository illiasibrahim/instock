from django.contrib.auth.models import User
from django.db import models

from core.models import CreatedByModel, DatedModel


class Category(CreatedByModel, DatedModel):
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=128)

    class Meta():
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class MedicineType(CreatedByModel, DatedModel):
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Medicine(CreatedByModel, DatedModel):
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=128)
    image = models.ImageField()
    chemical_name = models.CharField(max_length=128)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    type = models.ForeignKey(MedicineType, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Cluster(CreatedByModel, DatedModel):
    name = models.CharField(max_length=128)
    location = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Store(CreatedByModel, DatedModel):
    user = models.OneToOneField(
        User, on_delete=models.PROTECT,
        related_name="user_store")
    name = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
    address = models.CharField(max_length=256)
    cluster = models.ForeignKey(Cluster, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Stock(CreatedByModel, DatedModel):
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.store.name}-{self.medicine.name}"
