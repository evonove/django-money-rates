from __future__ import unicode_literals

import pytest

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


def test_fail_when_custom_backend_do_not_exists():
    with pytest.raises(CommandError) as exc:
        call_command("update_rates", "fake.custom.Backend")

    assert "Cannot find custom backend fake.custom.Backend. Is it correct" in str(exc.value)

@pytest.mark.django_db(transaction=True)
def test_custom_backend_used_when_specified():
    call_command("update_rates", "tests.test_commands.CustomBackend")

    assert 1 == RateSource.objects.filter(name="custom-backend").count()
    assert 2 == Rate.objects.filter(source__name="custom-backend").count()

@pytest.mark.django_db(transaction=True)
def test_default_backend_used_when_not_specified():
    """
    Test that if no backend is passed as parameter, the default one is used
    """
    money_rates_settings.DEFAULT_BACKEND = CustomBackend
    call_command("update_rates")

    assert 1 == RateSource.objects.filter(name="custom-backend").count()
    assert 2 == Rate.objects.filter(source__name="custom-backend").count()
