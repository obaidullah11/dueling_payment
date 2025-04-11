from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import PaymentTransaction
from .serializers import InitiatePaymentSerializer, PaymentTransactionSerializer
from .utils import generate_track_id, encrypt_aes, decrypt_aes, create_knet_request_data
import logging
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from .models import PaymentTransaction
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging
from .models import PaymentTransaction
import requests
from django.http import JsonResponse
from django.views import View
from django.http import JsonResponse, HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .utils import decrypt_aes
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from urllib.parse import parse_qs  # To parse URL-encoded data
from .utils import decrypt_aes
import base64
import json
logger = logging.getLogger(__name__)


# class InitiatePaymentView(APIView):
#     def post(self, request):
#         logger.info("Received request to initiate payment.")
#         serializer = InitiatePaymentSerializer(data=request.data)
#         if not serializer.is_valid():
#             logger.warning(f"Invalid request data: {serializer.errors}")
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Extract metadata from JSON body
#             user_id = str(request.data.get("user_id", ""))
#             tournament_id = str(request.data.get("tournament_id", ""))

#             # Encode metadata to base64 to avoid special character issues
#             metadata = json.dumps({"user_id": user_id, "tournament_id": tournament_id})
#             udf5 = base64.b64encode(metadata.encode()).decode()

#             # Create transaction record
#             track_id = generate_track_id()
#             logger.info(f"Generated track_id: {track_id}")
#             transaction = PaymentTransaction.objects.create(
#                 track_id=track_id,
#                 amount=serializer.validated_data['amount'],
#                 currency=serializer.validated_data['currency']
#             )
#             logger.info(f"Created transaction with ID: {transaction.id}")

#             # Prepare KNET request
#             payment_data = create_knet_request_data(
#                 track_id=track_id,
#                 amount=str(transaction.amount),
#                 udf1=serializer.validated_data.get('udf1', ''),
#                 udf2=serializer.validated_data.get('udf2', ''),
#                 udf3=serializer.validated_data.get('udf3', ''),
#                 udf4=serializer.validated_data.get('udf4', ''),
#                 udf5=udf5  # Base64 encoded user ID & tournament ID
#             )
#             logger.info(f"Prepared KNET request data: {payment_data}")

#             # Encrypt request data
#             encrypted_data = encrypt_aes(
#                 '&'.join(f"{k}={v}" for k, v in payment_data.items()),
#                 settings.KNET_SETTINGS['TERMINAL_RESOURCE_KEY']
#             )
#             logger.info("Successfully encrypted request data.")

#             # Create payment URL
#             payment_url = (
#                 f"{settings.KNET_SETTINGS['PAYMENT_URL']}?"
#                 f"param=paymentInit&trandata={encrypted_data}&"
#                 f"errorURL={payment_data['errorURL']}&"
#                 f"responseURL={payment_data['responseURL']}&"
#                 f"tranportalId={payment_data['id']}"
#             )
#             logger.info(f"Generated payment URL: {payment_url}")

#             return Response({
#                 'payment_url': payment_url,
#                 'track_id': track_id
#             })

#         except Exception as e:
#             logger.error(f"Payment initiation error: {str(e)}", exc_info=True)
#             return Response(
#                 {'error': 'Payment initiation failed'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

class InitiatePaymentView(APIView):
    def post(self, request):
        logger.info("Received request to initiate payment.")
        serializer = InitiatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid request data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Extract metadata from JSON body
            user_id = str(request.data.get("user_id", ""))
            user_name = str(request.data.get("user_name", ""))
            tournament_id = str(request.data.get("tournament_id", ""))
            tournament_name = str(request.data.get("tournament_name", ""))

            # Encode metadata to base64 to avoid special character issues
            metadata = json.dumps({
                "user_id": user_id,
                "user_name": user_name,
                "tournament_id": tournament_id,
                "tournament_name": tournament_name
            })
            udf5 = base64.b64encode(metadata.encode()).decode()

            # Set fixed amount
            fixed_amount = 50

            # Create transaction record
            track_id = generate_track_id()
            logger.info(f"Generated track_id: {track_id}")
            transaction = PaymentTransaction.objects.create(
                track_id=track_id,
                amount=fixed_amount,  # Fixed amount
                currency=serializer.validated_data['currency']
            )
            logger.info(f"Created transaction with ID: {transaction.id}")

            # Prepare KNET request
            payment_data = create_knet_request_data(
                track_id=track_id,
                amount=str(fixed_amount),  # Fixed amount
                udf1=serializer.validated_data.get('udf1', ''),
                udf2=serializer.validated_data.get('udf2', ''),
                udf3=serializer.validated_data.get('udf3', ''),
                udf4=serializer.validated_data.get('udf4', ''),
                udf5=udf5  # Base64 encoded metadata
            )
            logger.info(f"Prepared KNET request data: {payment_data}")

            # Encrypt request data
            encrypted_data = encrypt_aes(
                '&'.join(f"{k}={v}" for k, v in payment_data.items()),
                settings.KNET_SETTINGS['TERMINAL_RESOURCE_KEY']
            )
            logger.info("Successfully encrypted request data.")

            # Create payment URL
            payment_url = (
                f"{settings.KNET_SETTINGS['PAYMENT_URL']}?"
                f"param=paymentInit&trandata={encrypted_data}&"
                f"errorURL={payment_data['errorURL']}&"
                f"responseURL={payment_data['responseURL']}&"
                f"tranportalId={payment_data['id']}"
            )
            logger.info(f"Generated payment URL: {payment_url}")

            return Response({
                'payment_url': payment_url,
                'track_id': track_id
            })

        except Exception as e:
            logger.error(f"Payment initiation error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Payment initiation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# class InitiatePaymentView(APIView):
#     def post(self, request):
#         logger.info("Received request to initiate payment.")
#         serializer = InitiatePaymentSerializer(data=request.data)
#         if not serializer.is_valid():
#             logger.warning(f"Invalid request data: {serializer.errors}")
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Create transaction record
#             user_id = request.data.get("user_id", "")
#             tournament_id = request.data.get("tournament_id", "")
#             track_id = generate_track_id()
#             logger.info(f"Generated track_id: {track_id}")
#             transaction = PaymentTransaction.objects.create(
#                 track_id=track_id,
#                 amount=serializer.validated_data['amount'],
#                 currency=serializer.validated_data['currency']
#             )
#             logger.info(f"Created transaction with ID: {transaction.id}")

#             # Prepare KNET request
#             payment_data = create_knet_request_data(
#                 track_id=track_id,
#                 amount=str(transaction.amount),
#                 udf1=serializer.validated_data.get('udf1', ''),
#                 udf2=serializer.validated_data.get('udf2', ''),
#                 udf3=serializer.validated_data.get('udf3', ''),
#                 udf4=serializer.validated_data.get('udf4', ''),
#                 # udf5=serializer.validated_data.get('udf5', '')
#                 udf5=f"user_id:{user_id},tournament_id:{tournament_id}"
#             )
#             logger.info(f"Prepared KNET request data: {payment_data}")

#             # Encrypt request data
#             encrypted_data = encrypt_aes(
#                 '&'.join(f"{k}={v}" for k, v in payment_data.items()),
#                 settings.KNET_SETTINGS['TERMINAL_RESOURCE_KEY']
#             )
#             logger.info("Successfully encrypted request data.")

#             # Create payment URL
#             payment_url = (
#                 f"{settings.KNET_SETTINGS['PAYMENT_URL']}?"
#                 f"param=paymentInit&trandata={encrypted_data}&"
#                 f"errorURL={payment_data['errorURL']}&"
#                 f"responseURL={payment_data['responseURL']}&"
#                 f"tranportalId={payment_data['id']}"
#             )
#             logger.info(f"Generated payment URL: {payment_url}")

#             return Response({
#                 'payment_url': payment_url,
#                 'track_id': track_id
#             })

#         except Exception as e:
#             logger.error(f"Payment initiation error: {str(e)}", exc_info=True)
#             return Response(
#                 {'error': 'Payment initiation failed'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

# class InitiatePaymentView(APIView):
#     def post(self, request):
#         logger.info("Received request to initiate payment.")
#         serializer = InitiatePaymentSerializer(data=request.data)
#         if not serializer.is_valid():
#             logger.warning(f"Invalid request data: {serializer.errors}")
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Extract metadata from JSON body
#             user_id = request.data.get("user_id", "")
#             tournament_id = request.data.get("tournament_id", "")

#             # Create transaction record
#             track_id = generate_track_id()
#             logger.info(f"Generated track_id: {track_id}")
#             transaction = PaymentTransaction.objects.create(
#                 track_id=track_id,
#                 amount=serializer.validated_data['amount'],
#                 currency=serializer.validated_data['currency']
#             )
#             logger.info(f"Created transaction with ID: {transaction.id}")

#             # Prepare KNET request
#             payment_data = create_knet_request_data(
#                 track_id=track_id,
#                 amount=str(transaction.amount),
#                 udf1=serializer.validated_data.get('udf1', ''),
#                 udf2=serializer.validated_data.get('udf2', ''),
#                 udf3=serializer.validated_data.get('udf3', ''),
#                 udf4=serializer.validated_data.get('udf4', ''),
#                 udf5=f"user_id:{user_id},tournament_id:{tournament_id}"  # Metadata from request body
#             )
#             logger.info(f"Prepared KNET request data: {payment_data}")

#             # Encrypt request data
#             encrypted_data = encrypt_aes(
#                 '&'.join(f"{k}={v}" for k, v in payment_data.items()),
#                 settings.KNET_SETTINGS['TERMINAL_RESOURCE_KEY']
#             )
#             logger.info("Successfully encrypted request data.")

#             # Create payment URL
#             payment_url = (
#                 f"{settings.KNET_SETTINGS['PAYMENT_URL']}?"
#                 f"param=paymentInit&trandata={encrypted_data}&"
#                 f"errorURL={payment_data['errorURL']}&"
#                 f"responseURL={payment_data['responseURL']}&"
#                 f"tranportalId={payment_data['id']}"
#             )
#             logger.info(f"Generated payment URL: {payment_url}")

#             return Response({
#                 'payment_url': payment_url,
#                 'track_id': track_id
#             })

#         except Exception as e:
#             logger.error(f"Payment initiation error: {str(e)}", exc_info=True)
#             return Response(
#                 {'error': 'Payment initiation failed'},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

class PaymentErrorView(APIView):
    def post(self, request):
        try:
            # Log the incoming request for debugging
            logger.info(f"Received request at /error/ with content-type: {request.content_type}")
            logger.info(f"Request body: {request.data}")

            # Extract trandata from the request
            trandata = request.data.get('trandata', '')
            if not trandata:
                logger.error("Missing trandata in request")
                return Response(
                    {'error': 'Missing trandata'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Decrypt trandata
            try:
                decrypted_data = decrypt_aes(trandata, settings.KNET_SETTINGS['TERMINAL_RESOURCE_KEY'])
                logger.info(f"Decrypted trandata: {decrypted_data}")

                # Parse the decrypted URL-encoded data
                parsed_data = parse_qs(decrypted_data)
                logger.info(f"Parsed data: {parsed_data}")

                # Extract relevant fields from trandata
                payment_id = parsed_data.get('paymentid', [''])[0]
                result = parsed_data.get('result', [''])[0]
                track_id = parsed_data.get('trackid', [''])[0]
                amount = parsed_data.get('amt', [''])[0]
                transaction_id = parsed_data.get('tranid', [''])[0]
                error_code = parsed_data.get('Error', ['UNKNOWN_ERROR'])[0]
                error_text = parsed_data.get('ErrorText', ['No error text provided'])[0]

                # Log the extracted fields
                logger.info(f"Payment ID: {payment_id}, Result: {result}, Track ID: {track_id}, Amount: {amount}")

            except Exception as e:
                logger.error(f"Error decrypting or parsing trandata: {str(e)}")
                return Response(
                    {'error': 'Failed to decrypt or parse trandata'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Prepare error_data entirely based on trandata
            error_data = {
                'error_code': error_code,
                'error_text': error_text,
                'track_id': track_id,
                'payment_id': payment_id,
                'transaction_id': transaction_id,
                'amount': amount,
                'result': result,
                'timestamp': datetime.now().isoformat(),
            }

            # Log the extracted error data
            logger.error(f"Payment error received: {error_data}")

            # Update the transaction status in the database
            try:
                transaction = PaymentTransaction.objects.get(track_id=error_data['track_id'])
                transaction.status = PaymentTransaction.PaymentStatus.FAILED
                transaction.error_code = error_data['error_code']
                transaction.error_text = error_data['error_text']
                transaction.payment_id = error_data['payment_id']
                transaction.transaction_id = error_data['transaction_id']
                transaction.amount = error_data['amount']
                transaction.save()

                logger.info(f"Transaction {transaction.track_id} updated with error status.")
                return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

            except PaymentTransaction.DoesNotExist:
                logger.error(f"Transaction with track_id {error_data['track_id']} not found.")
                return Response(
                    {'error': f'Transaction with track_id {error_data["track_id"]} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            logger.exception("Unexpected error while processing payment error")
            return Response(
                {'error': 'Internal server error', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 # Ensure you have a decrypt_aes utility function


# @csrf_exempt
# def payment_response(request):
#     logger.info("Entering payment_response view")  # Debug log
#     logger.info(f"Received request at /response/ with content-type: {request.content_type}")

#     # Handle HTML requests
#     if request.content_type == "text/html":
#         try:
#             logger.info("Processing HTML request")  # Debug log
#             # Get the raw encrypted HTML content from the request body
#             encrypted_data = request.body.decode('utf-8')  # Decode the request body to a string
#             logger.info(f"Received encrypted HTML content: {encrypted_data}")

#             # Decrypt the content using your AES decryption utility
#             decrypted_data = decrypt_aes(encrypted_data, settings.KNET_SETTINGS['TERMINAL_RESOURCE_KEY'])
#             logger.info(f"Decrypted HTML content: {decrypted_data}")

#             # Parse the decrypted URL-encoded data
#             parsed_data = parse_qs(decrypted_data)
#             logger.info(f"Parsed data: {parsed_data}")

#             # Extract relevant fields
#             payment_id = parsed_data.get('paymentid', [''])[0]
#             result = parsed_data.get('result', [''])[0]
#             track_id = parsed_data.get('trackid', [''])[0]
#             amount = parsed_data.get('amt', [''])[0]

#             # Log the extracted fields
#             logger.info(f"Payment ID: {payment_id}, Result: {result}, Track ID: {track_id}, Amount: {amount}")

#             # Process the payment result
#             if result == "CAPTURED":
#                 response_message = f"<html><body><h1>Payment Successful</h1><p>Payment ID: {payment_id}</p><p>Amount: {amount}</p></body></html>"
#             else:
#                 response_message = f"<html><body><h1>Payment Failed</h1><p>Payment ID: {payment_id}</p><p>Reason: {result}</p></body></html>"

#             # Return the response as HTML
#             return HttpResponse(response_message, content_type="text/html")

#         except Exception as e:
#             logger.error(f"Error processing HTML content: {str(e)}")
#             return HttpResponse(
#                 "<html><body><h1>Error: Failed to process payment response</h1></body></html>",
#                 status=400,
#                 content_type="text/html"
#             )

#     # Handle unsupported content types
#     else:
#         logger.warning(f"Unsupported media type received: {request.content_type}")
#         return HttpResponse(
#             "<html><body><h1>Error: Unsupported Media Type</h1></body></html>",
#             status=415,
#             content_type="text/html"
#         )


# @csrf_exempt
# def payment_response(request):
#     """
#     Handle payment response from KNET.
#     KNET sends an encrypted response as raw data in the request body.
#     """
#     logger.info("Received payment response from KNET.")

#     try:
#         # Log the content type and raw request body
#         logger.info(f"Received request at /response/ with content-type: {request.content_type}")
#         raw_data = request.body.decode('utf-8')
#         logger.info(f"Raw request body: {raw_data}")

#         # Check if the content type is text/html
#         if request.content_type == "text/html":
#             logger.info("Processing HTML request")
#             encrypted_data = raw_data  # The raw body contains the encrypted data
#         else:
#             # Handle URL-encoded form data (if applicable)
#             parsed_data = parse_qs(raw_data)
#             encrypted_data = parsed_data.get('trandata', [''])[0]

#         if not encrypted_data:
#             logger.error("Missing trandata in payment response.")
#             return HttpResponse("REDIRECT=<Merchant Error URL>", status=400)

#         # Decrypt the trandata
#         decrypted_data = decrypt_aes(encrypted_data, settings.KNET_SETTINGS['TERMINAL_RESOURCE_KEY'])
#         logger.info(f"Decrypted trandata: {decrypted_data}")

#         # Parse the decrypted data
#         parsed_response = parse_qs(decrypted_data)
#         logger.info(f"Parsed response data: {parsed_response}")

#         # Extract relevant fields
#         payment_id = parsed_response.get('paymentid', [''])[0]
#         result = parsed_response.get('result', [''])[0]
#         track_id = parsed_response.get('trackid', [''])[0]
#         amount = parsed_response.get('amt', [''])[0]
#         auth_code = parsed_response.get('auth', [''])[0]
#         tran_id = parsed_response.get('tranid', [''])[0]
#         post_date = parsed_response.get('postdate', [''])[0]
#         udf1 = parsed_response.get('udf1', [''])[0]
#         udf2 = parsed_response.get('udf2', [''])[0]
#         udf3 = parsed_response.get('udf3', [''])[0]
#         udf4 = parsed_response.get('udf4', [''])[0]
#         udf5 = parsed_response.get('udf5', [''])[0]

#         # Log extracted fields
#         logger.info(f"Payment ID: {payment_id}, Result: {result}, Track ID: {track_id}, Amount: {amount}")

#         # Find the transaction in the database
#         try:
#             transaction = PaymentTransaction.objects.get(track_id=track_id)
#         except PaymentTransaction.DoesNotExist:
#             logger.error(f"Transaction with track_id {track_id} not found.")
#             return HttpResponse("REDIRECT=<Merchant Error URL>", status=404)

#         # Update the transaction with response details
#         transaction.payment_id = payment_id
#         transaction.status = result
#         transaction.auth_code = auth_code
#         transaction.tran_id = tran_id
#         transaction.post_date = post_date
#         transaction.udf1 = udf1
#         transaction.udf2 = udf2
#         transaction.udf3 = udf3
#         transaction.udf4 = udf4
#         transaction.udf5 = udf5
#         transaction.encrypted_response = encrypted_data  # Save encrypted response
#         transaction.decrypted_response = decrypted_data  # Save decrypted response
#         transaction.save()

#         logger.info(f"Transaction {track_id} updated with payment response.")

#         # Redirect to the merchant receipt page
#         receipt_url = f"{settings.MERCHANT_RECEIPT_URL}?track_id={track_id}&payment_id={payment_id}"
#         return HttpResponse(f"REDIRECT={receipt_url}")

#     except Exception as e:
#         logger.error(f"Error processing payment response: {str(e)}", exc_info=True)
#         return HttpResponse("REDIRECT=<Merchant Error URL>", status=500)
# import base64
# import json
# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# from urllib.parse import parse_qs
# import logging

# logger = logging.getLogger(__name__)

# @csrf_exempt
# def payment_response(request):
#     """
#     Handle payment response from KNET.
#     KNET sends an encrypted response as raw data in the request body.
#     """
#     logger.info("Received payment response from KNET.")

#     try:
#         # Log the content type and raw request body
#         logger.info(f"Received request at /response/ with content-type: {request.content_type}")
#         raw_data = request.body.decode('utf-8')
#         logger.info(f"Raw request body: {raw_data}")

#         # Check if the content type is text/html
#         if request.content_type == "text/html":
#             logger.info("Processing HTML request")
#             encrypted_data = raw_data  # The raw body contains the encrypted data
#         else:
#             # Handle URL-encoded form data (if applicable)
#             parsed_data = parse_qs(raw_data)
#             encrypted_data = parsed_data.get('trandata', [''])[0]

#         if not encrypted_data:
#             logger.error("Missing trandata in payment response.")
#             return HttpResponse("REDIRECT=<Merchant Error URL>", status=400)

#         # Decrypt the trandata
#         decrypted_data = decrypt_aes(encrypted_data, settings.KNET_SETTINGS['TERMINAL_RESOURCE_KEY'])
#         logger.info(f"Decrypted trandata: {decrypted_data}")

#         # Parse the decrypted data
#         parsed_response = parse_qs(decrypted_data)
#         logger.info(f"Parsed response data: {parsed_response}")

#         # Extract relevant fields
#         payment_id = parsed_response.get('paymentid', [''])[0]
#         result = parsed_response.get('result', [''])[0]
#         track_id = parsed_response.get('trackid', [''])[0]
#         amount = parsed_response.get('amt', [''])[0]
#         auth_code = parsed_response.get('auth', [''])[0]
#         tran_id = parsed_response.get('tranid', [''])[0]
#         post_date = parsed_response.get('postdate', [''])[0]
#         udf1 = parsed_response.get('udf1', [''])[0]
#         udf2 = parsed_response.get('udf2', [''])[0]
#         udf3 = parsed_response.get('udf3', [''])[0]
#         udf4 = parsed_response.get('udf4', [''])[0]
#         udf5_encoded = parsed_response.get('udf5', [''])[0]

#         # Decode Base64 UDF5
#         try:
#             decoded_udf5 = base64.b64decode(udf5_encoded).decode('utf-8')
#             udf5_data = json.loads(decoded_udf5)  # Convert back to dict
#             logger.info(f"Decoded udf5: {udf5_data}")
#         except Exception as e:
#             logger.error(f"Error decoding udf5: {str(e)}")
#             udf5_data = {}

#         user_id = udf5_data.get("user_id", "")
#         tournament_id = udf5_data.get("tournament_id", "")

#         # Log extracted fields
#         logger.info(f"Payment ID: {payment_id}, Result: {result}, Track ID: {track_id}, Amount: {amount}")

#         # Find the transaction in the database
#         try:
#             transaction = PaymentTransaction.objects.get(track_id=track_id)
#         except PaymentTransaction.DoesNotExist:
#             logger.error(f"Transaction with track_id {track_id} not found.")
#             return HttpResponse("REDIRECT=<Merchant Error URL>", status=404)

#         # Update the transaction with response details
#         transaction.payment_id = payment_id
#         transaction.status = result
#         transaction.auth_code = auth_code
#         transaction.tran_id = tran_id
#         transaction.post_date = post_date
#         transaction.udf1 = udf1
#         transaction.udf2 = udf2
#         transaction.udf3 = udf3
#         transaction.udf4 = udf4
#         transaction.udf5 = decoded_udf5  # Save decoded JSON data
#         transaction.user_id = user_id  # Store extracted user_id
#         transaction.tournament_id = tournament_id  # Store extracted tournament_id
#         transaction.encrypted_response = encrypted_data  # Save encrypted response
#         transaction.decrypted_response = decrypted_data  # Save decrypted response
#         transaction.save()

#         logger.info(f"Transaction {track_id} updated with payment response.")

#         # Redirect to the merchant receipt page
#         receipt_url = f"{settings.MERCHANT_RECEIPT_URL}?track_id={track_id}&payment_id={payment_id}"
#         return HttpResponse(f"REDIRECT={receipt_url}")

#     except Exception as e:
#         logger.error(f"Error processing payment response: {str(e)}", exc_info=True)
#         return HttpResponse("REDIRECT=<Merchant Error URL>", status=500)
import base64
import json
import logging
import requests  # Import requests for API call
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import parse_qs
from django.conf import settings
from .models import PaymentTransaction  # Ensure correct model import

logger = logging.getLogger(__name__)

@csrf_exempt
def payment_response(request):
    """
    Handle payment response from KNET.
    """
    logger.info("Received payment response from KNET.")

    try:
        logger.info(f"Received request at /response/ with content-type: {request.content_type}")
        raw_data = request.body.decode('utf-8')
        logger.info(f"Raw request body: {raw_data}")

        # Extract encrypted data
        encrypted_data = raw_data if request.content_type == "text/html" else parse_qs(raw_data).get('trandata', [''])[0]

        if not encrypted_data:
            logger.error("Missing trandata in payment response.")
            return HttpResponse("REDIRECT=<Merchant Error URL>", status=400)

        # Decrypt data
        decrypted_data = decrypt_aes(encrypted_data, settings.KNET_SETTINGS['TERMINAL_RESOURCE_KEY'])
        parsed_response = parse_qs(decrypted_data)

        # Extract required fields
        track_id = parsed_response.get('trackid', [''])[0]
        result = parsed_response.get('result', [''])[0]
        payment_id = parsed_response.get('paymentid', [''])[0]
        auth_code = parsed_response.get('auth', [''])[0]
        tran_id = parsed_response.get('tranid', [''])[0]
        post_date = parsed_response.get('postdate', [''])[0]
        udf5_encoded = parsed_response.get('udf5', [''])[0]

        # Decode UDF5
        try:
            decoded_udf5 = base64.b64decode(udf5_encoded).decode('utf-8')
            udf5_data = json.loads(decoded_udf5)
            logger.info(f"Decoded udf5: {udf5_data}")
        except Exception as e:
            logger.error(f"Error decoding udf5: {str(e)}")
            udf5_data = {}

        user_id = udf5_data.get("user_id", 0)
        tournament_id = udf5_data.get("tournament_id", 0)

        logger.info(f"Processing transaction for Track ID: {track_id}, User ID: {user_id}, Tournament ID: {tournament_id}")

        # Update transaction in the database
        try:
            transaction = PaymentTransaction.objects.get(track_id=track_id)
        except PaymentTransaction.DoesNotExist:
            logger.error(f"Transaction with track_id {track_id} not found.")
            return HttpResponse("REDIRECT=<Merchant Error URL>", status=404)

        transaction.payment_id = payment_id
        transaction.status = result
        transaction.auth_code = auth_code
        transaction.tran_id = tran_id
        transaction.post_date = post_date
        transaction.udf5 = decoded_udf5
        transaction.user_id = user_id
        transaction.tournament_id = tournament_id
        transaction.encrypted_response = encrypted_data
        transaction.decrypted_response = decrypted_data
        transaction.save()

        logger.info(f"Transaction {track_id} updated successfully.")

        # Determine payment status
        payment_status = "paid" if result.lower() == "captured" else "failed"

        # Send PATCH request to update payment status
        api_url = "https://dueling.pythonanywhere.com/update-payment-status/"
        payload = {
            "user_id": user_id,
            "tournament_id": tournament_id,
            "payment_status": payment_status
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.patch(api_url, json=payload, headers=headers)
            if response.status_code in [200, 204]:  # 204 means no content but success
                logger.info(f"Successfully updated payment status: {payment_status}")
            else:
                logger.error(f"Failed to update payment status. Response: {response.text}")
        except requests.RequestException as e:
            logger.error(f"Error sending PATCH request: {str(e)}")

        # Redirect to merchant receipt page
        receipt_url = f"{settings.MERCHANT_RECEIPT_URL}?track_id={track_id}&payment_id={payment_id}"
        return HttpResponse(f"REDIRECT={receipt_url}")

    except Exception as e:
        logger.error(f"Error processing payment response: {str(e)}", exc_info=True)
        return HttpResponse("REDIRECT=<Merchant Error URL>", status=500)


@csrf_exempt
def receipt_page(request):
    """
    Merchant Receipt Page to display transaction details to the customer.
    """
    # Get query parameters
    track_id = request.GET.get('track_id')
    payment_id = request.GET.get('payment_id')

    # Fetch the transaction from the database
    transaction = get_object_or_404(PaymentTransaction, track_id=track_id, payment_id=payment_id)

    # Prepare context for the template
    context = {
        'transaction': transaction,
    }

    # Render the receipt page
    return render(request, 'receipt.html', context)