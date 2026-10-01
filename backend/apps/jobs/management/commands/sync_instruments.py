from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.instruments.models import Instrument
from apps.jobs.models import JobRun
from apps.jobs.services import tracked_job
from providers.capabilities import ProviderCapability
from providers.runtime import build_provider_registry


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--symbols",
            help="Optional comma-separated symbols; omit to fetch the configured provider universe",
        )
        parser.add_argument("--exchange", default="NASDAQ")

    def handle(self, *args, **options):
        if options["symbols"]:
            symbols = sorted(
                {
                    symbol.strip()
                    for symbol in options["symbols"].upper().split(",")
                    if symbol.strip()
                }
            )
            if any(not symbol.replace(".", "").replace("-", "").isalnum() for symbol in symbols):
                raise CommandError("Invalid symbol")
            incoming = [
                {
                    "symbol": symbol,
                    "exchange": options["exchange"].upper(),
                    "name": symbol,
                    "asset_type": "stock",
                    "currency": "USD",
                    "provider_symbol": symbol,
                    "is_active": True,
                }
                for symbol in symbols
            ]
            provider_name = "manual"
        else:
            provider = build_provider_registry().get_provider(ProviderCapability.SYMBOL_UNIVERSE)
            incoming = [
                {
                    "symbol": item.symbol,
                    "exchange": item.exchange,
                    "name": item.name,
                    "asset_type": item.asset_type,
                    "currency": item.currency,
                    "provider_symbol": item.provider_symbol,
                    "is_active": item.is_active,
                }
                for item in provider.get_symbol_universe()
            ]
            provider_name = provider.name

        keys = {(item["symbol"], item["exchange"]) for item in incoming}
        existing = set(
            Instrument.objects.filter(symbol__in={symbol for symbol, _ in keys}).values_list(
                "symbol", "exchange"
            )
        )
        objects = [Instrument(**item) for item in incoming]
        with tracked_job(JobRun.JobType.INSTRUMENT_SYNC, symbols_requested=len(objects)) as job:
            with transaction.atomic():
                Instrument.objects.bulk_create(
                    objects,
                    update_conflicts=True,
                    unique_fields=["symbol", "exchange"],
                    update_fields=[
                        "name",
                        "asset_type",
                        "currency",
                        "provider_symbol",
                        "is_active",
                        "updated_at",
                    ],
                )
            job.rows_inserted = len(keys - existing)
            job.rows_updated = len(keys & existing)
            job.symbols_succeeded = len(objects)
            job.metadata = {"provider": provider_name}

        self.stdout.write(
            self.style.SUCCESS(
                f"Instrument sync complete: {len(objects)} active US assets, "
                f"{job.rows_inserted} inserted, {job.rows_updated} updated, "
                f"provider={provider_name}"
            )
        )
