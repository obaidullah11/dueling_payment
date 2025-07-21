from django.urls import path
# from .views import initiate_payment, payment_response, payment_error
from .views import *
# urlpatterns = [
#     path('payment/initiate/', initiate_payment, name='initiate_payment'),
#     path('payment/response/', payment_response, name='payment_response'),
#     path('payment/error/', payment_error, name='payment_error'),
# ]
# URL Patterns
urlpatterns = [
   path('api/payment/', create_charge, name='make_payment'),
   path('payment/result/', payment_result, name='payment_result'),
   path('payment/post_result/', post_payment_result, name='post_payment_result'),
   path('api/scrape-images/', scrape_pinterest_images),
]