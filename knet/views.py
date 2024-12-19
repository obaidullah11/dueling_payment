from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
import uuid
from Crypto.Cipher import AES
import base64
from .models import KnetTransaction
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)


def generate_track_id():
    """
    Generate a unique track ID for each transaction.
    """
    track_id = str(uuid.uuid4())[:8]
    logger.info(f"Generated new track ID: {track_id}")
    return track_id


class KnetPayment:
    TRANPORTAL_ID = "540801"
    TRANPORTAL_PASSWORD = "540801pg"
    TERMINAL_RESOURCE_KEY = "9D2JJ07HA1Y47RF3"
    # Correct test URL for RAW method
    TEST_URL = "https://kpaytest.com.kw/kpg/PaymentHTTP.htm"

    def encrypt_AES(self, data):
        try:
            logger.debug(f"Starting AES encryption for data length: {len(data)}")
            key = self.TERMINAL_RESOURCE_KEY.encode('utf-8')
            cipher = AES.new(key, AES.MODE_CBC, key)
            pad_length = 16 - (len(data) % 16)
            padded_data = data + (chr(pad_length) * pad_length)
            encrypted = cipher.encrypt(padded_data.encode('utf-8'))
            result = base64.b64encode(encrypted).decode('utf-8')
            logger.debug("AES encryption completed successfully")
            return result
        except Exception as e:
            logger.error(f"AES encryption failed: {str(e)}")
            raise


@csrf_exempt
def initiate_payment(request):
    if request.method == 'POST':
        try:
            logger.info("Starting new payment initiation")
            data = json.loads(request.body)
            amount = "{:.3f}".format(float(data.get('amount', '0')))
            track_id = generate_track_id()

            logger.info(f"Processing payment - Amount: {amount}, Track ID: {track_id}")

            knet = KnetPayment()
            
            # Build absolute URLs
            response_url = 'https://mfarhanakram.eu.pythonanywhere.com/payment/response/'
            error_url = 'https://mfarhanakram.eu.pythonanywhere.com/payment/error/'

            # Build request string in correct order
            request_string = (
                # f"id={knet.TRANPORTAL_ID}"
                f"amt={amount}&"
                f"action=1&"
                f"responseURL={response_url}&"
                f"errorURL={error_url}&"
                f"trackid={track_id}&"
                f"udf1=test1&"
                f"udf2=test2&"
                f"udf3=test3&"
                f"udf4=test4&"
                f"udf5=test5&"
                f"currencycode=414&"
                f"langid=USA&"
                f"id={knet.TRANPORTAL_ID}&"
                f"password={knet.TRANPORTAL_PASSWORD}"
                f"errorURL={error_url}&"
                f"responseURL={response_url}&"
            )

            logger.debug(f"Built request string: {request_string}")
            encrypted_data = knet.encrypt_AES(request_string)

            # Build payment URL - simplified for direct redirect
            # payment_url = (
            #     f"{knet.TEST_URL}?"
            #     f"param=paymentInit&"
            #     f"trandata={encrypted_data}"
            #     f"tranportalId={knet.TRANPORTAL_ID}"
            # )
            payment_url = (
                f"{knet.TEST_URL}?"
                f"param=paymentInit&"
                f"trandata={encrypted_data}&"
                f"errorURL={error_url}&"
                f"responseURL={response_url}&"
                f"tranportalId={knet.TRANPORTAL_ID}"
            )

            logger.info(f"Created payment URL for track ID: {track_id}")

            # Store initial transaction
            transaction = KnetTransaction.objects.create(
                track_id=track_id,
                amount=amount,
                status='INITIATED'
            )
            logger.info(f"Stored initial transaction record for track ID: {track_id}")

            # Return URL for redirect
            return JsonResponse({
                'success': True,
                'payment_url': payment_url,
                'track_id': track_id
            })

        except Exception as e:
            logger.error(f"Payment initiation failed: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)
@csrf_exempt
def payment_response(request):
    """
    Handles the notification from KNET (server-to-server)
    """
    logger.info("Received payment response from KNET")
    try:
        # Get the encrypted response from the output stream
        trandata = request.POST.get('trandata')
        
        if trandata:
            logger.debug("Processing trandata from KNET response")
            knet = KnetPayment()
            decrypted_data = knet.decrypt_AES(trandata)
            
            # Parse the response
            params = dict(item.split('=') for item in decrypted_data.split('&'))
            
            # Get track_id from response
            track_id = params.get('trackid')
            
            logger.info(f"Processing payment response for track ID: {track_id}")
            
            # Update transaction in database
            transaction = KnetTransaction.objects.filter(track_id=track_id).first()
            if transaction:
                transaction.result = params.get('result')
                transaction.payment_id = params.get('paymentid')
                transaction.auth = params.get('auth')
                transaction.ref = params.get('ref')
                transaction.tran_id = params.get('tranid')
                transaction.encrypted_response = trandata
                transaction.decrypted_response = decrypted_data
                transaction.save()
                logger.info(f"Updated transaction record for track ID: {track_id}")

            # Generate receipt URL
            receipt_url = request.build_absolute_uri(
                f'/payment/receipt/{track_id}/'
            )
            logger.info(f"Generated receipt URL for track ID: {track_id}")

            # Return REDIRECT as required
            return HttpResponse(f"REDIRECT={receipt_url}")
            
        logger.warning("No transaction data received in payment response")
        return HttpResponse("No transaction data received", status=400)

    except Exception as e:
        logger.error(f"Payment response processing failed: {str(e)}")
        return HttpResponse("Error processing payment", status=500)
        
        
@csrf_exempt
def payment_error(request):
    """
    Handles KNET payment errors and returns JSON response
    """
    logger.info("Received payment error from KNET")
    try:
        # Get error parameters
        error_code = request.GET.get('Error', '')
        error_text = request.GET.get('ErrorText', '')
        track_id = request.GET.get('trackid', '')

        logger.error(f"Payment error - Track ID: {track_id}, Error: {error_code}, Message: {error_text}")

        # Update transaction if track_id exists
        if track_id:
            transaction = KnetTransaction.objects.filter(track_id=track_id).first()
            if transaction:
                transaction.result = 'ERROR'
                transaction.error_code = error_code
                transaction.error_text = error_text
                transaction.save()
                logger.info(f"Updated transaction record with error details for track ID: {track_id}")

        # Return JSON response
        return JsonResponse({
            'status': 'error',
            'error_code': error_code,
            'error_text': error_text,
            'track_id': track_id,
            'timestamp': datetime.now().isoformat(),
            'debug': {
                'query_params': dict(request.GET.items()),
                'headers': dict(request.headers)
            }
        }, status=400)

    except Exception as e:
        logger.error(f"Error handling payment error: {str(e)}")
        # Return system error
        return JsonResponse({
            'status': 'error',
            'error_code': 'SYSTEM_ERROR',
            'error_text': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)

