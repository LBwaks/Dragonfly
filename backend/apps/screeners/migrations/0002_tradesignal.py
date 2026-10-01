import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("instruments", "0002_instrument_latest_price_and_more"),
        ("screeners", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TradeSignal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "horizon",
                    models.CharField(
                        choices=[("DAILY", "Daily"), ("WEEKLY", "Weekly"), ("MONTHLY", "Monthly")],
                        max_length=10,
                    ),
                ),
                (
                    "case_type",
                    models.CharField(
                        choices=[("BULL", "Bull case"), ("BEAR", "Bear case")], max_length=10
                    ),
                ),
                ("as_of_date", models.DateField()),
                ("price", models.DecimalField(decimal_places=6, max_digits=20)),
                ("score", models.FloatField()),
                ("technical_score", models.FloatField()),
                ("fundamental_score", models.FloatField()),
                ("macro_score", models.FloatField()),
                ("pattern_score", models.FloatField()),
                ("data_completeness", models.FloatField(default=0)),
                ("candle_patterns", models.JSONField(blank=True, default=list)),
                ("chart_patterns", models.JSONField(blank=True, default=list)),
                ("rationale", models.JSONField(blank=True, default=list)),
                ("calculation_version", models.CharField(max_length=50)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "instrument",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="trade_signals",
                        to="instruments.instrument",
                    ),
                ),
            ],
            options={"ordering": ["-score", "instrument__symbol"]},
        ),
        migrations.AddConstraint(
            model_name="tradesignal",
            constraint=models.UniqueConstraint(
                fields=("instrument", "horizon"), name="uq_trade_signal_instrument_horizon"
            ),
        ),
        migrations.AddIndex(
            model_name="tradesignal",
            index=models.Index(
                fields=["case_type", "horizon", "-score"], name="signal_case_horizon_idx"
            ),
        ),
    ]
