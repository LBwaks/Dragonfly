from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        for command in [
            "sync_instruments",
            "sync_instrument_overviews",
            "ingest_market_data",
            "validate_market_data",
            "calculate_technicals",
            "rebuild_technical_snapshot",
            "generate_trade_signals",
            "run_screeners",
        ]:
            self.stdout.write(f"Starting {command}")
            call_command(command)
