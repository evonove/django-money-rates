from __future__ import unicode_literals
from decimal import Decimal

from .exceptions import CurrencyConversionException
from .models import Rate, RateSource
from .settings import money_rates_settings

import moneyed


def get_rate(currency):
    """Returns the rate from the default currency to `currency`."""
    backend = money_rates_settings.DEFAULT_BACKEND()
    source_name = backend.get_source_name()
    try:
        return Rate.objects.get_rate_value(
            source_name=source_name,
            currency=currency)
    except Rate.DoesNotExist:
        raise CurrencyConversionException(
            "Rate for %s in %s do not exists. "
            "Please run python manage.py update_rates" % (
                currency, source_name))


def get_rate_source():
    """Get the default Rate Source and return it."""
    backend = money_rates_settings.DEFAULT_BACKEND()
    try:
        return RateSource.objects.get(name=backend.get_source_name())
    except RateSource.DoesNotExist:
        raise CurrencyConversionException(
            "Rate for %s source do not exists. "
            "Please run python manage.py update_rates" % backend.get_source_name()) # NOQA


def get_rate_source_base_currency():
    """Get the default Rate Source and return it."""
    backend = money_rates_settings.DEFAULT_BACKEND()
    try:
        return RateSource.objects.get_source_base_currency(
            source_name=backend.get_source_name())
    except RateSource.DoesNotExist:
        raise CurrencyConversionException(
            "Rate for %s source do not exists. "
            "Please run python manage.py update_rates" % backend.get_source_name()) # NOQA


def base_convert_money(amount, currency_from, currency_to):
    """
    Convert 'amount' from 'currency_from' to 'currency_to'
    """
    source_base_currency = get_rate_source_base_currency()

    # Get rate for currency_from.
    if source_base_currency != currency_from:
        rate_from = get_rate(currency_from)
    else:
        # If currency from is the same as base currency its rate is 1.
        rate_from = Decimal(1)

    # Get rate for currency_to.
    rate_to = get_rate(currency_to)

    if isinstance(amount, float):
        amount = Decimal(amount).quantize(Decimal('.000001'))

    # After finishing the operation, quantize down final amount to two points.
    return ((amount / rate_from) * rate_to).quantize(Decimal("1.00"))


def convert_money(amount, currency_from, currency_to):
    """
    Convert 'amount' from 'currency_from' to 'currency_to' and return a Money
    instance of the converted amount.
    """
    # assign new_amount to amount in case of no convertion, avoid useless else
    new_amount = amount
    # if the currency is the same, avoid convert nothing
    if str(currency_from) != str(currency_to):
        new_amount = base_convert_money(amount, currency_from, currency_to)
    return moneyed.Money(new_amount, currency_to)
