from django.contrib import admin

from core.admin import BaseAdmin
from orders.models import Rider, Order, OrderItem


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


admin.site.register(Rider, RiderAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
