from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils.timezone import now
from .models import Settlement
from datetime import timedelta

@receiver(post_save, sender=Settlement)
def send_payment_reminder(sender, instance, **kwargs):
    """Send an email if payment is pending and the due date is in one week."""
    if instance.status == "pending" and instance.due_date == (now().date() + timedelta(days=7)):
        subject = "🔔 Payment Due Reminder"
        message = (
            f"Dear {instance.user.username},\n\n"
            f"Your payment of ${instance.amount} is due today ({instance.due_date}). "
            "Please complete the payment to avoid any late fees.\n\n"
            "Thank you."
        )
        send_mail(
            subject=subject,
            message=message,
            from_email="pocketsense@collage.com",
            recipient_list=[instance.user.email],
            fail_silently=False,
        )
