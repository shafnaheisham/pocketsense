from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Settlement


@receiver(post_save, sender=Settlement)
def update_settlement_status(sender, instance, created, **kwargs):
    """
    Signal to update the settlement status to 'Paid' after a payment is successful.
    """
    # Check if the settlement already exists and the payment was marked as 'Success'
    if not created and instance.payment_status == "Success":
        try:
            # Update the settlement status to 'Paid'
            instance.status = "Paid"
            instance.save(update_fields=["status"])
            print(f"Settlement {instance.id} status updated to 'Paid'.")
        except Exception as e:
            print(f"Error updating settlement status for Settlement {instance.id}: {e}")
