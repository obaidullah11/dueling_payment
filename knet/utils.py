
### 5. Utils (payment/utils.py)

import secrets
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.conf import settings
from base64 import b64encode
import logging

logger = logging.getLogger(__name__)

def generate_track_id():
    """Generate a unique track ID for the transaction"""
    return f"TRK{secrets.token_hex(8).upper()}"

def encrypt_aes(data: str, key: str) -> str:
    try:
        cipher = AES.new(
            key.encode('utf-8'),
            AES.MODE_CBC,
            key.encode('utf-8')
        )
        padded_data = pad(data.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return encrypted.hex().upper()
    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        raise

def decrypt_aes(encrypted_data: str, key: str) -> str:
    try:
        cipher = AES.new(
            key.encode('utf-8'),
            AES.MODE_CBC,
            key.encode('utf-8')
        )
        encrypted_bytes = bytes.fromhex(encrypted_data)
        decrypted = cipher.decrypt(encrypted_bytes)
        unpadded = unpad(decrypted, AES.block_size)
        return unpadded.decode('utf-8')
    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        raise

def create_knet_request_data(
    track_id: str,
    amount: str,
    udf1: str = '',
    udf2: str = '',
    udf3: str = '',
    udf4: str = '',
    udf5: str = ''
):
    """Create KNET payment request data"""
    return {
        'trackid': track_id,
        'amt': amount,
        'id': settings.KNET_SETTINGS['TRANPORTAL_ID'],
        'password': settings.KNET_SETTINGS['TRANPORTAL_PASSWORD'],
        'currencycode': '414',  # KWD
        'langid': 'EN',
        'action': '1',  # Purchase action
        'responseURL': settings.KNET_SETTINGS['RESPONSE_URL'],
        'errorURL': settings.KNET_SETTINGS['ERROR_URL'],
        'udf1': udf1,
        'udf2': udf2,
        'udf3': udf3,
        'udf4': udf4,
        'udf5': udf5,
    }



def log_payment_error(error_data: dict):
    """Log payment errors for monitoring and debugging"""
    logger.error(
        "Payment Error: Code=%s, Text=%s, TrackID=%s",
        error_data.get('error_code'),
        error_data.get('error_text'),
        error_data.get('track_id')
    )