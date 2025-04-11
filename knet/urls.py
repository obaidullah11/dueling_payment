
### 7. URLs (payment/urls.py)

from django.urls import path
from .views import InitiatePaymentView, payment_response,PaymentErrorView,receipt_page

app_name = 'payment'

urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('response/', payment_response, name='payment-response'),
    path('error/', PaymentErrorView.as_view(), name='payment-error'),
    path('receipt/', receipt_page, name='receipt-page'),
    # path('tcg/<str:game_name>/', TCGCardView.as_view(), name='tcg_cards'),
]
