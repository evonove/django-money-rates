from __future__ import unicode_literals

from decimal import Decimal
import unittest

from django.core.exceptions import ImproperlyConfigured

from mock import patch

from djmoney_rates.backends import BaseRateBackend, RateBackendError, OpenExchangeBackend
from djmoney_rates.models import Rate, RateSource
from djmoney_rates.settings import money_rates_settings


class BaseTest(unittest.TestCase):
    def tearDown(self):
        RateSource.objects.all().delete()
        Rate.objects.all().delete()


class TestRateBackends(BaseTest):
    def test_source_name_empty_is_invalid(self):
        self.assertRaises(RateBackendError, BaseRateBackend().get_source_name)

    def test_update_rates(self):
        class RateBackend(BaseRateBackend):
            source_name = "a source"
            base_currency = "EUR"

            def get_rates(self):
                return {"EUR": 1, "USD": 0.2222, "PLN": 0.3333}

        backend = RateBackend()
        backend.update_rates()

        self.assertEqual(3, Rate.objects.filter(source__name="a source").count())


class TestOpenExchangeBackend(BaseTest):
    test_data_1 = b"""{"disclaimer": "Exchange rates provided by [...]",
        "license": "Data collected and blended [...]", "timestamp": 1319730758, "base": "USD",
        "rates": {"AED": 3.672626, "AFN": 48.3775, "ALL": 110.223333, "AMD": 409.604993,
        "YER": 215.035559, "ZAR": 8.416205, "ZMK": 4954.411262, "ZWL": 322.355011}}"""

    test_data_2 = b"""{"disclaimer": "Exchange rates provided by [...]",
        "license": "Data collected and blended [...]", "timestamp": 1319730758, "base": "USD",
        "rates": {"AED": 4.672626, "AFN": 48.3775, "ALL": 110.223333, "AMD": 409.604993,
        "YER": 215.035559, "ZAR": 8.416205, "ZMK": 4954.411262, "ZWL": 322.355011}}"""

    def setUp(self):
        money_rates_settings.OPENEXCHANGE_URL = "http://openexchangerates.org/api/latest.json"
        money_rates_settings.OPENEXCHANGE_APP_ID = "fake-app-id"

    def test_missing_url_error(self):
        money_rates_settings.OPENEXCHANGE_URL = ""

        self.assertRaises(ImproperlyConfigured, OpenExchangeBackend)

    def test_missing_app_id(self):
        money_rates_settings.OPENEXCHANGE_APP_ID = ""

        self.assertRaises(ImproperlyConfigured, OpenExchangeBackend)

    def test_url_is_correct(self):
        backend = OpenExchangeBackend()
        self.assertEqual(backend.url, "http://openexchangerates.org/api/latest.json?app_id=fake-app-id&base=USD")

    @patch("djmoney_rates.backends.urlopen")
    def test_rates_are_saved(self, urlopen_mock):
        backend = OpenExchangeBackend()

        instance = urlopen_mock.return_value
        instance.read.return_value = self.test_data_1
        backend.update_rates()

        self.assertEqual(8, Rate.objects.filter(source__name=backend.get_source_name()).count())

    @patch("djmoney_rates.backends.urlopen")
    def test_rates_are_updated(self, urlopen_mock):
        backend = OpenExchangeBackend()

        instance = urlopen_mock.return_value
        instance.read.return_value = self.test_data_1
        backend.update_rates()

        first_update = RateSource.objects.get(name=backend.get_source_name()).last_update
        self.assertEqual(8, Rate.objects.filter(source__name=backend.get_source_name()).count())
        self.assertEqual(Decimal("3.672626"), Rate.objects.get(currency="AED").value)

        # change return value for mocked urlopen read call
        instance.read.return_value = self.test_data_2

        # call update rates again
        backend.update_rates()

        last_update = RateSource.objects.get(name=backend.get_source_name()).last_update

        self.assertEqual(8, Rate.objects.filter(source__name=backend.get_source_name()).count())
        self.assertTrue(last_update > first_update)
        self.assertEqual(Decimal("4.672626"), Rate.objects.get(currency="AED").value)
