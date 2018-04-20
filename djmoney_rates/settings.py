from __future__ import unicode_literals

"""
This module is largely inspired by django-rest-framework settings.

Settings for django-money-rates are all namespaced in the DJANGO_MONEY_RATES setting.
For example your project's `settings.py` file might look like this:

DJANGO_MONEY_RATES = {
    'DEFAULT_BACKEND': 'djmoney_rates.backends.OpenExchangeBackend',
}

This module provides the `money_rates_settings` object, that is used to access
django-money-rates settings, checking for user settings first, then falling
back to the defaults.
"""

from django.conf import settings
from django.utils import six
from django.utils.module_loading import import_module



USER_SETTINGS = getattr(settings, 'DJANGO_MONEY_RATES', None)

DEFAULTS = {
    'DEFAULT_BACKEND': 'djmoney_rates.backends.OpenExchangeBackend',

    'OPENEXCHANGE_URL': 'http://openexchangerates.org/api/latest.json',
    'OPENEXCHANGE_APP_ID': '',
    'OPENEXCHANGE_BASE_CURRENCY': 'USD',
}

# List of settings that cannot be empty
MANDATORY = (
    'DEFAULT_BACKEND',
)

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    'DEFAULT_BACKEND',
)


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if isinstance(val, six.string_types):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        msg = "Could not import '%s' for setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class MoneyRatesSettings(object):
    """
    A settings object, that allows Bazaar settings to be accessed as properties.

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(self, user_settings=None, defaults=None, import_strings=None, mandatory=None):
        self.user_settings = user_settings or {}
        self.defaults = defaults or {}
        self.import_strings = import_strings or ()
        self.mandatory = mandatory or ()

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid django-money-rates setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if val and attr in self.import_strings:
            val = perform_import(val, attr)

        self.validate_setting(attr, val)

        # Cache the result
        setattr(self, attr, val)
        return val

    def validate_setting(self, attr, val):
        if not val and attr in self.mandatory:
            raise AttributeError("django-money-rates setting: '%s' is mandatory" % attr)


money_rates_settings = MoneyRatesSettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS, MANDATORY)
