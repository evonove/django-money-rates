from __future__ import unicode_literals

from decimal import Decimal

from .exceptions import CurrencyConversionException
from .models import Rate, RateSource
from .settings import money_rates_settings


def convert_money(amount, currency_from, currency_to):
    """
    Convert 'amount' from 'currency_from' to 'currency_to'
    """

def get_rate(currency):
    """Returns the rate from the default currency to `currency`."""
    source = get_rate_source()
    try:
        return Rate.objects.get(source=source, currency=currency).value
    except Rate.DoesNotExist:
        raise CurrencyConversionException(
            "Rate for %s in %s do not exists. "
            "Please run python manage.py update_rates" % (
                currency, source.name))


def get_rate_source():
    """Get the default Rate Source and return it."""
    backend = money_rates_settings.DEFAULT_BACKEND()
    try:
        source = RateSource.objects.get(name=backend.get_source_name())
        return RateSource.objects.get(name=backend.get_source_name())
    except RateSource.DoesNotExist:
        raise CurrencyConversionException(
            "Rate for %s source do not exists. "
            "Please run python manage.py update_rates" % backend.get_source_name())

    # get rate for currency_from
    source = get_rate_source()

    # Get rate for currency_from.
    if source.base_currency != currency_from:
        rate_from = get_rate(currency_from)
    else:
        # If currency from is the same as base currency its rate is 1.
        rate_from = Decimal(1)

    # Get rate for currency_to.
    rate_to = get_rate(currency_to)

    if isinstance(amount, float):
        amount = Decimal(amount).quantize(Decimal('.000001'))

    return (amount / rate_from) * rate_to
