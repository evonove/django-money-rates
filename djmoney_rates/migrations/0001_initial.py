# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('currency', models.CharField(max_length=3)),
                ('value', models.DecimalField(max_digits=20, decimal_places=6)),
            ],
        ),
        migrations.CreateModel(
            name='RateSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('base_currency', models.CharField(max_length=3)),
            ],
        ),
        migrations.AddField(
            model_name='rate',
            name='source',
            field=models.ForeignKey(to='djmoney_rates.RateSource'),
        ),
        migrations.AlterUniqueTogether(
            name='rate',
            unique_together=set([('source', 'currency')]),
        ),
    ]
