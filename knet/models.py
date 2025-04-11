from django.db import models

class PaymentTransaction(models.Model):
    track_id = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=3)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=20, blank=True, null=True)
    payment_id = models.CharField(max_length=50, blank=True, null=True)
    auth_code = models.CharField(max_length=50, blank=True, null=True)
    tran_id = models.CharField(max_length=50, blank=True, null=True)
    post_date = models.CharField(max_length=50, blank=True, null=True)
    udf1 = models.CharField(max_length=255, blank=True, null=True)
    udf2 = models.CharField(max_length=255, blank=True, null=True)
    udf3 = models.CharField(max_length=255, blank=True, null=True)
    udf4 = models.CharField(max_length=255, blank=True, null=True)
    udf5 = models.CharField(max_length=255, blank=True, null=True)
    encrypted_response = models.TextField(blank=True, null=True)
    decrypted_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.track_id}"