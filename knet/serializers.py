
### 4. Serializers (payment/serializers.py)

from rest_framework import serializers
from .models import PaymentTransaction

class InitiatePaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=3)
    currency = serializers.CharField(default='KWD')

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = '__all__'

