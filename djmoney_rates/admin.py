from django.contrib import admin
from .models import Rate, RateSource


class RateInline(admin.TabularInline):
    model = Rate


@admin.register(RateSource)
class RateSourceAdmin(admin.ModelAdmin):
    inlines = [
        RateInline,
    ]


