=============================
django-money-rates
=============================

.. image:: https://badge.fury.io/py/django-money-rates.png
    :target: http://badge.fury.io/py/django-money-rates
    
.. image:: https://travis-ci.org/evonove/django-money-rates.png?branch=master
        :target: https://travis-ci.org/evonove/django-money-rates


.. image:: https://coveralls.io/repos/evonove/django-money-rates/badge.png
  :target: https://coveralls.io/r/evonove/django-money-rates

.. image:: https://pypip.in/d/django-money-rates/badge.png
        :target: https://crate.io/packages/django-money-rates?version=latest


Currency conversion for money

Documentation
-------------

The full documentation is at https://django-money-rates.readthedocs.io/.

Quickstart
----------

Install django-money-rates::

    pip install django-money-rates

Then use it in a project::

    import djmoney_rates

In order to save exchange rates to your database, add `djmoney_rates` to your INSTALLED_APPS in your project's settings::

    INSTALLED_APPS = (
        ...
        'djmoney_rates',
        ...
    )

Setup the Open Exchange Rates backend
-------------------------------------

Open an account at https://openexchangerates.org/ if you don't have one already. Then, add this to your project's settings::

    DJANGO_MONEY_RATES = {
        'DEFAULT_BACKEND': 'djmoney_rates.backends.OpenExchangeBackend',
        'OPENEXCHANGE_URL': 'http://openexchangerates.org/api/latest.json',
        'OPENEXCHANGE_APP_ID': 'YOUR APP ID HERE',
        'OPENEXCHANGE_BASE_CURRENCY': 'USD',
    }

For more information on the Open Exchange Rates API, see https://openexchangerates.org/

Pull the latest Exchange Rates
------------------------------

Once your backend is setup, get the latest exchange rates::

    $ ./manage.py update_rates

Convert from one currency to another
------------------------------------

Here's an example of converting 10 Euros to Brazilian Reais:

.. code-block:: python

    from moneyed import Money
    from djmoney_rates.utils import convert_money
    brl_money = convert_money(10, "EUR", "BRL")

Features
--------

* Convert money from one currency to another with an easy to use API.

TODO List
---------

* Add money converter wrapper for util's `convert_money` function.
* Add celery periodic task for getting daily exchange rates.
