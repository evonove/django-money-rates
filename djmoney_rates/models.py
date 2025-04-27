from django.db import models
from django.utils.translation import gettext_lazy as _


class RateSource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    last_update = models.DateTimeField(auto_now=True)
    base_currency = models.CharField(max_length=3)

    def __str__(self):
        return _("%s rates in %s update %s") % (
            self.name, self.base_currency, self.last_update)


class Rate(models.Model):
    source = models.ForeignKey(RateSource, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3)
    value = models.DecimalField(max_digits=20, decimal_places=6)

    class Meta:
        unique_together = ('source', 'currency')

    def __str__(self):
        return _("%s at %.6f") % (self.currency, self.value)
