from __future__ import unicode_literals

import unittest

from django.core.management import call_command
from django.core.management.base import CommandError

from djmoney_rates.backends import BaseRateBackend
from djmoney_rates.models import Rate, RateSource
from djmoney_rates.settings import money_rates_settings


class CustomBackend(BaseRateBackend):
    source_name = "custom-backend"
    base_currency = "USD"

    def get_rates(self):
        return {"PLN": 3.07, "EUR": 0.74}


class TestCommands(unittest.TestCase):
    def test_fail_when_custom_backend_do_not_exists(self):
        with self.assertRaises(CommandError):
            call_command("update_rates", "fake.custom.Backend")

    def test_custom_backend_used_when_specified(self):
        call_command("update_rates", "tests.test_commands.CustomBackend")

        self.assertEqual(1, RateSource.objects.filter(name="custom-backend").count())
        self.assertEqual(2, Rate.objects.filter(source__name="custom-backend").count())

    def test_default_backend_used_when_not_specified(self):
        """
        Test that if no backend is passed as parameter, the default one is used
        """
        money_rates_settings.DEFAULT_BACKEND = CustomBackend
        call_command("update_rates")

        self.assertEqual(1, RateSource.objects.filter(name="custom-backend").count())
        self.assertEqual(2, Rate.objects.filter(source__name="custom-backend").count())
