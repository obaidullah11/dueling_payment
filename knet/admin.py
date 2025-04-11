from django.contrib import admin
from .models import PaymentTransaction

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the PaymentTransaction model.
    """
    # Fields to display in the list view
    list_display = (
        'track_id',
        'amount',
        'currency',
        'status',
        'payment_id',
        'created_at',
        'updated_at',
        'udf5',
    )

    # Fields to filter by in the right sidebar
    list_filter = (
        'status',
        'currency',
        'created_at',
    )

    # Fields to search by in the search bar
    search_fields = (
        'track_id',
        'payment_id',
        'tran_id',
    )

    # Fields to display in the detail view
    fieldsets = (
        ('Transaction Details', {
            'fields': (
                'track_id',
                'amount',
                'currency',
                'status',
                'payment_id',
                'auth_code',
                'tran_id',
                'post_date',
            ),
        }),
        ('UDF Fields', {
            'fields': (
                'udf1',
                'udf2',
                'udf3',
                'udf4',
                'udf5',
            ),
        }),
        ('Response Data', {
            'fields': (
                'encrypted_response',
                'decrypted_response',
            ),
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
        }),
    )

    # Make the created_at and updated_at fields read-only
    readonly_fields = (
        'created_at',
        'updated_at',
    )