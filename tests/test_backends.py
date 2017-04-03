from __future__ import unicode_literals

from decimal import Decimal
import pytest

from django.core.exceptions import ImproperlyConfigured

from mock import patch

from djmoney_rates.backends import BaseRateBackend, RateBackendError, OpenExchangeBackend
from djmoney_rates.models import Rate, RateSource
from djmoney_rates.settings import money_rates_settings


@pytest.fixture
def custom_data():
    return [
        b"""{"disclaimer": "Exchange rates provided by [...]",
        "license": "Data collected and blended [...]", "timestamp": 1319730758, "base": "USD",
        "rates": {"AED": 3.672626, "AFN": 48.3775, "ALL": 110.223333, "AMD": 409.604993,
        "YER": 215.035559, "ZAR": 8.416205, "ZMK": 4954.411262, "ZWL": 322.355011}}""",
        b"""{"disclaimer": "Exchange rates provided by [...]",
        "license": "Data collected and blended [...]", "timestamp": 1319730758, "base": "USD",
        "rates": {"AED": 4.672626, "AFN": 48.3775, "ALL": 110.223333, "AMD": 409.604993,
        "YER": 215.035559, "ZAR": 8.416205, "ZMK": 4954.411262, "ZWL": 322.355011}}"""
    ]

@pytest.fixture
def set_up():
    money_rates_settings.OPENEXCHANGE_URL = "http://openexchangerates.org/api/latest.json"
    money_rates_settings.OPENEXCHANGE_APP_ID = "fake-app-id"

def test_source_name_empty_is_invalid():
    with pytest.raises(RateBackendError) as exc:
        BaseRateBackend().get_source_name()

    assert "'source_name' can't be empty or you should override 'get_source_name'" in str(exc.value)

def test_base_currency_empty_is_invalid():
    with pytest.raises(RateBackendError) as exc:
        BaseRateBackend().get_base_currency()

    assert "'base_currency' can't be empty or you should override 'get_base_currency'" in str(exc.value)

@pytest.mark.django_db(transaction=True)
def test_update_rates():
    class RateBackend(BaseRateBackend):
        source_name = "a source"
        base_currency = "EUR"

        def get_rates(self):
            return {"EUR": 1, "USD": 0.2222, "PLN": 0.3333}

    backend = RateBackend()
    backend.update_rates()

    assert 3 == Rate.objects.filter(source__name="a source").count()

def test_missing_url_error(set_up):
    money_rates_settings.OPENEXCHANGE_URL = ""

    with pytest.raises(ImproperlyConfigured) as exc:
        OpenExchangeBackend()

    assert "OPENEXCHANGE_URL setting should not be empty when using OpenExchangeBackend" in str(exc.value)

def test_missing_app_id(set_up):
    money_rates_settings.OPENEXCHANGE_APP_ID = ""

    with pytest.raises(ImproperlyConfigured) as exc:
        OpenExchangeBackend()

    assert "OPENEXCHANGE_APP_ID setting should not be empty when using OpenExchangeBackend" in str(exc.value)

def test_url_is_correct(set_up):
    backend = OpenExchangeBackend()
    assert backend.url == "http://openexchangerates.org/api/latest.json?app_id=fake-app-id&base=USD"

@pytest.mark.django_db(transaction=True)
def test_rates_are_saved(set_up, custom_data, mocker):
    backend = OpenExchangeBackend()
    urlopen_mock = mocker.patch("djmoney_rates.backends.urlopen")

    instance = urlopen_mock.return_value
    instance.read.return_value = custom_data[0]
    backend.update_rates()

    assert 8 == Rate.objects.filter(source__name=backend.get_source_name()).count()

@pytest.mark.django_db(transaction=True)
def test_rates_are_updated(set_up, custom_data, mocker):
    backend = OpenExchangeBackend()
    urlopen_mock = mocker.patch("djmoney_rates.backends.urlopen")

    instance = urlopen_mock.return_value
    instance.read.return_value = custom_data[0]
    backend.update_rates()

    first_update = RateSource.objects.get(name=backend.get_source_name()).last_update
    assert 8 == Rate.objects.filter(source__name=backend.get_source_name()).count()
    assert Decimal("3.672626") == Rate.objects.get(currency="AED").value

    # change return value for mocked urlopen read call
    instance.read.return_value = custom_data[1]

    # call update rates again
    backend.update_rates()

    last_update = RateSource.objects.get(name=backend.get_source_name()).last_update

    assert 8 == Rate.objects.filter(source__name=backend.get_source_name()).count()
    assert last_update > first_update
    assert Decimal("4.672626") == Rate.objects.get(currency="AED").value
