from __future__ import unicode_literals
from django.core.cache import cache
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class CacheRateSourceManager(models.Manager):

    def _get_cache_key(self, source_name):
        return "dj_money_rate__ratesource__{}".format(source_name)

    def get_source_base_currency(self, source_name):
        cache_key = self._get_cache_key(source_name)
        base_currency = cache.get(cache_key)
        if base_currency is None:
            base_currency = RateSource.objects.get(
                name=source_name).base_currency
            cache.set(cache_key, base_currency)  # cache for 'ever'
        return base_currency

    def set_base_currency(self, source_rate):
        cache_key = self._get_cache_key(source_rate.name)
        cache.set(cache_key, source_rate.base_currency)  # cache for 'ever'

    def clear_base_currency(self, source_rate):
        cache_key = self._get_cache_key(source_rate.name)
        cache.delete(cache_key)


@python_2_unicode_compatible
class RateSource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    last_update = models.DateTimeField(auto_now=True)
    base_currency = models.CharField(max_length=3)
    objects = CacheRateSourceManager()

    def __str__(self):
        return _("%s rates in %s update %s") % (
            self.name, self.base_currency, self.last_update)


@receiver(post_save, sender=RateSource)
def update_rate_source_cache(sender, instance, created, **kwargs):
    RateSource.objects.set_base_currency(instance)


@receiver(post_delete, sender=RateSource)
def delete_rate_cache(sender, instance, created, **kwargs):
    RateSource.objects.clear_base_currency(instance)


class CacheRateManager(models.Manager):

    def _get_cache_key(self, source_name, currency):
        return "dj_money_rate__rate__{}__{}".format(source_name, currency)

    def get_rate_value(self, source_name, currency):
        cache_key = self._get_cache_key(source_name, currency)
        rate_value = cache.get(cache_key)
        if rate_value is None:
            rate_value = Rate.objects.get(
                source__name=source_name,
                currency=currency).value
            cache.set(cache_key, rate_value)  # cache for 'ever'
        return rate_value

    def set_rate_value(self, rate):
        cache_key = self._get_cache_key(rate.source.name, rate.currency)
        cache.set(cache_key, rate.value)  # cache for 'ever'

    def clear_rate_value(self, rate):
        cache_key = self._get_cache_key(rate.source.name, rate.currency)
        cache.delete(cache_key)


@python_2_unicode_compatible
class Rate(models.Model):
    source = models.ForeignKey(RateSource, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3)
    value = models.DecimalField(max_digits=20, decimal_places=6)
    objects = CacheRateManager()

    class Meta:
        unique_together = ('source', 'currency')

    def __str__(self):
        return _("%s at %.6f") % (self.currency, self.value)


@receiver(post_save, sender=Rate)
def update_rate_cache(sender, instance, created, **kwargs):
    Rate.objects.set_rate_value(instance)


@receiver(post_delete, sender=Rate)
def delete_rate_cache(sender, instance, created, **kwargs):
    Rate.objects.clear_rate_value(instance)
