
### 6. Views (payment/views.py)

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import PaymentTransaction
from .serializers import InitiatePaymentSerializer, PaymentTransactionSerializer
from .utils import generate_track_id, encrypt_aes, decrypt_aes, create_knet_request_data
import logging

logger = logging.getLogger(__name__)

class InitiatePaymentView(APIView):
    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create transaction record
            track_id = generate_track_id()
            transaction = PaymentTransaction.objects.create(
                track_id=track_id,
                amount=serializer.validated_data['amount'],
                currency=serializer.validated_data['currency']
            )

            # Prepare KNET request
            payment_data = create_knet_request_data(
                track_id=track_id,
                amount=str(transaction.amount)
            )

            # Encrypt request data
            encrypted_data = encrypt_aes(
                '&'.join(f"{k}={v}" for k, v in payment_data.items()),
                settings.KNET_SETTINGS['TERMINAL_RESOURCE_KEY']
            )

            # Create payment URL
            payment_url = (
                f"{settings.KNET_SETTINGS['PAYMENT_URL']}?"
                f"param=paymentInit&trandata={encrypted_data}&"
                f"errorURL={payment_data['errorURL']}&"
                f"responseURL={payment_data['responseURL']}&"
                f"tranportalId={payment_data['id']}"
            )

            return Response({
                'payment_url': payment_url,
                'track_id': track_id
            })

        except Exception as e:
            logger.error(f"Payment initiation error: {str(e)}")
            return Response(
                {'error': 'Payment initiation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentResponseView(APIView):
    def post(self, request):
        try:
            error_text = request.data.get('ErrorText')
            error_no = request.data.get('Error')
            encrypted_data = request.data.get('trandata')

            if not error_text and not error_no and encrypted_data:
                # Decrypt response
                decrypted_data = decrypt_aes(
                    encrypted_data,
                    settings.KNET_SETTINGS['TERMINAL_RESOURCE_KEY']
                )

                # Parse response data
                response_params = dict(param.split('=') for param in decrypted_data.split('&'))
                
                # Update transaction
                transaction = PaymentTransaction.objects.get(
                    track_id=response_params.get('trackid')
                )
                transaction.payment_id = response_params.get('paymentid')
                transaction.transaction_id = response_params.get('tranid')
                transaction.reference_id = response_params.get('ref')
                transaction.status = (
                    PaymentTransaction.PaymentStatus.SUCCESSFUL 
                    if response_params.get('result') == 'CAPTURED'
                    else PaymentTransaction.PaymentStatus.FAILED
                )
                transaction.response_data = response_params
                transaction.save()

            else:
                # Handle error response
                transaction = PaymentTransaction.objects.get(
                    track_id=request.data.get('trackid')
                )
                transaction.status = PaymentTransaction.PaymentStatus.FAILED
                transaction.error_code = error_no
                transaction.error_text = error_text
                transaction.save()

            serializer = PaymentTransactionSerializer(transaction)
            return Response(serializer.data)

        except PaymentTransaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Payment response error: {str(e)}")
            return Response(
                {'error': 'Payment response processing failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

