from __future__ import unicode_literals

from .exceptions import CurrencyConversionException
from .models import Rate, RateSource
from .settings import money_rates_settings


def convert_money(amount, currency_from, currency_to):
    """
    Convert 'amount' from 'currency_from' to 'currency_to'
    """
    backend = money_rates_settings.DEFAULT_BACKEND()

    try:
        source = RateSource.objects.get(name=backend.get_source_name())
    except RateSource.DoesNotExist:
        raise CurrencyConversionException(
            "Rate for %s source do not exists. "
            "Please run python manage.py update_rates" % backend.get_source_name())

    # get rate for currency_from
    if source.base_currency != currency_from:
        try:
            rate_from = Rate.objects.get(source=source, currency=currency_from)
        except Rate.DoesNotExist:
            raise CurrencyConversionException(
                "Rate for %s in %s do not exists. "
                "Please run python manage.py update_rates" % (
                    currency_from, source.name))
    else:
        # If currency from is the same as base currency its rate is 1
        rate_from = 1

    # get rate for currency_to
    try:
        rate_to = Rate.objects.get(source=source, currency=currency_to)
    except Rate.DoesNotExist:
        raise CurrencyConversionException(
            "Rate for %s in %s do not exists. "
            "Please run python manage.py update_rates" % (
                currency_to, source.name))

    return (amount / rate_from.value) * rate_to.value
