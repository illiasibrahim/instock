from django.urls import path

from api.v1.views import GetToken, MedicineListAPIView, CreateOrderView, ValidateLocationView

urlpatterns = [
    path('token/', GetToken.as_view(), name='api_token_auth'),
    path('medicines/', MedicineListAPIView.as_view(), name='medicine-list'),
    path('location/validate/', ValidateLocationView.as_view(), name='validate-location'),
    path('orders/', CreateOrderView.as_view(), name='create-order')
]
