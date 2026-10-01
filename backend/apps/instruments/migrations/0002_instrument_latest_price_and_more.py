from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("instruments", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="instrument",
            name="latest_price",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=20, null=True
            ),
        ),
        migrations.AddField(
            model_name="instrument",
            name="price_as_of",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="instrument",
            name="price_provider",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
