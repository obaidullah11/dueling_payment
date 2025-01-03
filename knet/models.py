from django.db import models
from django.utils.translation import gettext_lazy as _

class PaymentTransaction(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SUCCESSFUL = 'SUCCESSFUL', _('Successful')
        FAILED = 'FAILED', _('Failed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    track_id = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=3)
    currency = models.CharField(max_length=3, default='KWD')
    payment_id = models.CharField(max_length=50, null=True, blank=True)
    transaction_id = models.CharField(max_length=50, null=True, blank=True)
    reference_id = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    error_code = models.CharField(max_length=50, null=True, blank=True)
    error_text = models.TextField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.track_id} - {self.amount} {self.currency}"

    class Meta:
        ordering = ['-created_at']