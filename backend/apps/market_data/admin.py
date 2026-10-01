from django.contrib import admin

from . import models

for model in [
    models.DailyBar,
    models.CorporateAction,
    models.DataQualityEvent,
    models.InstrumentSnapshot,
    models.FundamentalSnapshot,
    models.PeerRelationship,
    models.CompanyNews,
    models.MarketNews,
    models.SecFiling,
    models.InsiderTransaction,
    models.InsiderSentiment,
    models.AnalystRecommendation,
    models.EarningsEvent,
    models.EarningsResult,
    models.IpoEvent,
    models.DomainFreshness,
]:
    admin.site.register(model)
