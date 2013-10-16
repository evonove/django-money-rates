from __future__ import unicode_literals

import logging
import json

from django.core.exceptions import ImproperlyConfigured
from django.utils import six

from .compat import urlopen
from .exceptions import RateBackendError
from .models import RateSource, Rate
from .settings import money_rates_settings


logger = logging.getLogger(__name__)


class RateBackend(object):
    source_name = None

    def get_source_name(self):
        if not self.source_name:
            raise RateBackendError("'source_name' should not be empty")

        return self.source_name

    def update_rates(self):
        """
        Creates or updates rates for a source
        """
        source = RateSource.objects.get_or_create(name=self.get_source_name())
        source.base_currency = self.base_currency
        source.save()

        for currency, value in six.iteritems(self.get_rates()):
            rate = Rate.objects.get_or_create(source=source, currency=currency)
            rate.value = value
            rate.save()

    def get_rates(self):
        """
        Should return a dictionary that maps currency code with its rate value
        """


class OpenExchangeBackend(RateBackend):
    source_name = "openexchange.org"

    def __init__(self):
        if not money_rates_settings.OPENEXCHANGE_URL:
            raise ImproperlyConfigured(
                "OPENEXCHANGE_URL setting should not be empty when using OpenExchangeBackend")

        if not money_rates_settings.OPENEXCHANGE_APP_ID:
            raise ImproperlyConfigured(
                "OPENEXCHANGE_APP_ID setting should not be empty when using OpenExchangeBackend")

        # Build the base api url
        base_url = "%s?app_id=%s" % (money_rates_settings.OPENEXCHANGE_URL,
                                     money_rates_settings.OPENEXCHANGE_APP_ID)

        # Change the base currency whether it is specified in settings
        if money_rates_settings.OPENEXCHANGE_BASE_CURRENCY:
            base_url += "&base=%s" % money_rates_settings.OPENEXCHANGE_BASE_CURRENCY

        self.url = base_url

    def get_rates(self):
        try:
            logger.debug("Connecting to url %s" % self.url)
            data = urlopen(self.url).read()
            return json.loads(data)['rates']

        except Exception as e:
            logger.exception("Error retrieving data from %s", self.url)
            raise RateBackendError("Error retrieving rates: %s" % e)
