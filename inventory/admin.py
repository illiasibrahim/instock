from django.contrib import admin

from core.admin import BaseAdmin
from inventory.models import Category, MedicineType, Medicine, Cluster, Store, Stock


class CategoryAdmin(BaseAdmin):
    list_display = (
        "__str__", "code", "created_date", "created_by"
    )
    model = Category


class MedicineTypeAdmin(BaseAdmin):
    list_display = (
        "__str__", "code", "created_date", "created_by"
    )
    model = Category


class MedicineAdmin(BaseAdmin):
    list_display = (
        "__str__", "code", "created_date", "created_by"
    )
    model = MedicineType


class ClusterAdmin(BaseAdmin):
    list_display = (
        "__str__", "location", "created_date", "created_by"
    )
    model = Cluster


class StoreAdmin(BaseAdmin):
    list_display = (
        "__str__", "location", "created_date", "created_by"
    )
    model = Store


class StockAdmin(BaseAdmin):
    list_display = (
        "__str__", "store", "created_date", "created_by"
    )
    model = Stock


admin.site.register(Category, CategoryAdmin)
admin.site.register(MedicineType, MedicineTypeAdmin)
admin.site.register(Medicine, MedicineAdmin)
admin.site.register(Cluster, ClusterAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Stock, StockAdmin)
