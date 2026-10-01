from django.contrib import admin

from .models import Screener, ScreenerMatch, ScreenerRun, ScreeningSnapshot, TradeSignal

admin.site.register(Screener)
admin.site.register(ScreenerRun)
admin.site.register(ScreenerMatch)
admin.site.register(ScreeningSnapshot)
admin.site.register(TradeSignal)
