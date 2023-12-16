from django.urls import path

from orders.admin_views.views import OrderAcceptView

urlpatterns = [
    path('accept/', OrderAcceptView.as_view(), name='order_accept_view'),
]
