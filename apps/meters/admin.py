from django.contrib import admin

from meters.models import House, Flat, WaterMeter, MeterValues, Tariff, Calculations

# Register your models here.
admin.site.register(House)
admin.site.register(Flat)
admin.site.register(WaterMeter)
admin.site.register(MeterValues)
admin.site.register(Tariff)
admin.site.register(Calculations)

