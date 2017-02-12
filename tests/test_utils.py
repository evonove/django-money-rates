from __future__ import unicode_literals

from decimal import Decimal

import pytest

from djmoney_rates.backends import BaseRateBackend
from djmoney_rates.exceptions import CurrencyConversionException
from djmoney_rates.models import RateSource, Rate
from djmoney_rates.settings import money_rates_settings
from djmoney_rates.utils import base_convert_money, convert_money

import moneyed

@pytest.fixture
def set_up():
    class RateBackend(BaseRateBackend):
        source_name = "fake-backend"
        base_currency = "USD"

    money_rates_settings.DEFAULT_BACKEND = RateBackend

@pytest.mark.django_db(transaction=True)
def test_base_conversion_fail_when_source_does_not_exist(set_up):
    with pytest.raises(CurrencyConversionException) as cm:
        base_convert_money(10.0, "PLN", "EUR")

    assert "Rate for fake-backend source do not exists" in str(cm.value)

@pytest.mark.django_db(transaction=True)
def test_base_conversion_fail_when_currency_from_does_not_exist(set_up):
    RateSource.objects.create(name="fake-backend")

    with pytest.raises(CurrencyConversionException) as cm:
        base_convert_money(10.0, "PLN", "EUR")

    assert "Rate for PLN in fake-backend do not exists" in str(cm.value)

@pytest.mark.django_db(transaction=True)
def test_base_conversion_fail_when_currency_to_does_not_exist(set_up):
    source = RateSource.objects.create(name="fake-backend")
    Rate.objects.create(source=source, currency="PLN", value=0.99999)

    with pytest.raises(CurrencyConversionException) as cm:
        base_convert_money(10.0, "PLN", "EUR")

    assert "Rate for EUR in fake-backend do not exists" in str(cm.value)

@pytest.mark.django_db(transaction=True)
def test_base_conversion_works_from_base_currency(set_up):
    source = RateSource.objects.create(name="fake-backend", base_currency="USD")
    Rate.objects.create(source=source, currency="USD", value=1)
    Rate.objects.create(source=source, currency="EUR", value=0.74)

    amount = base_convert_money(1, "USD", "EUR")
    assert amount == Decimal("0.74")

@pytest.mark.django_db(transaction=True)
def test_base_conversion_is_working_from_other_currency(set_up):
    source = RateSource.objects.create(name="fake-backend", base_currency="USD")
    Rate.objects.create(source=source, currency="PLN", value=3.07)
    Rate.objects.create(source=source, currency="EUR", value=0.74)

    amount = base_convert_money(10.0, "PLN", "EUR")
    assert amount == Decimal("2.41")

@pytest.mark.django_db(transaction=True)
def test_conversion_fail_when_source_does_not_exist(set_up):
    with pytest.raises(CurrencyConversionException) as cm:
        convert_money(10.0, "PLN", "EUR")

    assert "Rate for fake-backend source do not exists" in str(cm.value)

@pytest.mark.django_db(transaction=True)
def test_conversion_fail_when_currency_from_does_not_exist(set_up):
    RateSource.objects.create(name="fake-backend")

    with pytest.raises(CurrencyConversionException) as cm:
        convert_money(10.0, "PLN", "EUR")

    assert "Rate for PLN in fake-backend do not exists" in str(cm.value)

@pytest.mark.django_db(transaction=True)
def test_conversion_fail_when_currency_to_does_not_exist(set_up):
    source = RateSource.objects.create(name="fake-backend")
    Rate.objects.create(source=source, currency="PLN", value=0.99999)

    with pytest.raises(CurrencyConversionException) as cm:
        convert_money(10.0, "PLN", "EUR")

    assert "Rate for EUR in fake-backend do not exists" in str(cm.value)

@pytest.mark.django_db(transaction=True)
def test_conversion_works_from_base_currency(set_up):
    source = RateSource.objects.create(name="fake-backend", base_currency="USD")
    Rate.objects.create(source=source, currency="USD", value=1)
    Rate.objects.create(source=source, currency="EUR", value=0.74)

    amount = convert_money(1, "USD", "EUR")
    assert type(amount) == moneyed.Money
    assert amount == moneyed.Money(Decimal("0.74"), "EUR")

@pytest.mark.django_db(transaction=True)
def test_conversion_is_working_from_other_currency(set_up):
    source = RateSource.objects.create(name="fake-backend", base_currency="USD")
    Rate.objects.create(source=source, currency="PLN", value=3.07)
    Rate.objects.create(source=source, currency="EUR", value=0.74)

    amount = convert_money(10.0, "PLN", "EUR")
    assert amount == moneyed.Money(Decimal("2.41"), "EUR")
