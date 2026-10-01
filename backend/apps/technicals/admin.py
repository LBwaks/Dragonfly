from django.contrib import admin

from .models import TechnicalDaily, TechnicalSnapshot

admin.site.register(TechnicalDaily)
admin.site.register(TechnicalSnapshot)
