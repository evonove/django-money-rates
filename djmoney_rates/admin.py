from django.contrib import admin
from .models import Rate, RateSource


class RateInline(admin.TabularInline):
    model = Rate


class RateSourceAdmin(admin.ModelAdmin):
    inlines = [
        RateInline,
    ]


admin.site.register(RateSource, RateSourceAdmin)
