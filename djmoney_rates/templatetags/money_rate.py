# -*- coding: utf-8 -*-
from decimal import Decimal
from django import template
from djmoney_rates.utils import convert_money
from utils.money import MoneyPatched

register = template.Library()


class ChangeCurrencyNode(template.Node):

    def __init__(self, price, price_currency, dest_currency, decimal=None):
        self.price = template.Variable(price)
        self.price_currency = template.Variable(price_currency)
        self.currency = template.Variable(dest_currency)
        self.decimal = None
        if decimal:
            self.decimal = template.Variable(decimal)

    def render(self, context):
        price = self.price.resolve(context)
        if not isinstance(price, Decimal):
            price = Decimal(price)
        try:
            money = convert_money(
                price,
                self.price_currency.resolve(context),
                self.currency.resolve(context)
            )
            patched_money = MoneyPatched._patch_to_current_class(money)
            if self.decimal:
                patched_money.decimal_places = self.decimal.resolve(context)
            return patched_money
        except template.VariableDoesNotExist:
            return ''


@register.tag(name='change_currency')
def change_currency(parser, token):
    try:
        params = token.split_contents()
        tag_name = params[0]
        current_price = params[1]
        current_currency = params[2]
        new_currency = params[3]
        decimal = None
        if len(params) > 4:
            decimal = params[4]

    except ValueError:
        tag_name = token.contents.split()[0]
        raise template.TemplateSyntaxError(
            '%r tag requires exactly two arguments' % (tag_name))
    return ChangeCurrencyNode(current_price, current_currency, new_currency,
                              decimal)
