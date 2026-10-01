from django.core.management.base import BaseCommand

from apps.instruments.models import Instrument
from apps.screeners.services import rebuild_screening_snapshot


class Command(BaseCommand):
    def handle(self, *args, **options):
        count = sum(
            rebuild_screening_snapshot(instrument) is not None
            for instrument in Instrument.objects.filter(is_active=True)
        )
        self.stdout.write(self.style.SUCCESS(f"Rebuilt {count} screening snapshots"))
