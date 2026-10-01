from django.contrib import admin

from .models import Instrument


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ("symbol", "name", "exchange", "sector", "is_active", "updated_at")
    list_filter = ("exchange", "sector", "industry", "is_active")
    search_fields = ("symbol", "name")
    ordering = ("symbol", "exchange")
