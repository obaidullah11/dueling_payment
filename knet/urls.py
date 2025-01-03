
### 7. URLs (payment/urls.py)

from django.urls import path
from .views import InitiatePaymentView, PaymentResponseView

app_name = 'payment'

urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('response/', PaymentResponseView.as_view(), name='payment-response'),
]
