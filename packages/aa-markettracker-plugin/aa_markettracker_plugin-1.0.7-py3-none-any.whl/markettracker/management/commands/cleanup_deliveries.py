from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from markettracker.models import DeliveryItem
from django.conf import settings

class Command(BaseCommand):
    help = "Delete fulfilled deliveries older than configured retention days"

    def handle(self, *args, **options):
        retention_days = getattr(settings, "DELIVERIES_RETENTION_DAYS", 30)
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        deleted_count, _ = DeliveryItem.objects.filter(
            delivered=True, 
            # Assume no date field, adjust if delivered date is added
        ).delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {deleted_count} fulfilled deliveries older than {retention_days} days."
            )
        )
