from django.contrib import admin

from core.admin import BaseAdmin
from orders.models import Rider, Order, OrderItem, Bucket, BucketItem, Customer


class RiderAdmin(BaseAdmin):
    list_display = (
        "__str__", "user", "created_date", "created_by"
    )
    model = Rider


class OrderAdmin(BaseAdmin):
    list_display = (
        "__str__", "code", "created_date", "created_by"
    )
    model = Order


class OrderItemAdmin(BaseAdmin):
    list_display = (
        "__str__", "medicine", "quantity", "created_date"
    )
    model = OrderItem
    readonly_fields = ("created_date", "modified_date")


class BucketAdmin(BaseAdmin):
    list_display = (
        "__str__", "rider", "is_active", "created_date"
    )
    model = Bucket
    readonly_fields = ("created_date", "modified_date")


class BucketItemAdmin(BaseAdmin):
    list_display = (
        "__str__", "bucket", "order", "created_date"
    )
    model = BucketItem
    readonly_fields = ("created_date", "modified_date")


class CustomerAdmin(BaseAdmin):
    list_display = (
        "__str__", "user", "userEID", "created_date"
    )
    model = Customer
    readonly_fields = ("created_date", "modified_date")


admin.site.register(Rider, RiderAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Bucket, BucketAdmin)
admin.site.register(BucketItem, BucketItemAdmin)
admin.site.register(Customer, CustomerAdmin)
