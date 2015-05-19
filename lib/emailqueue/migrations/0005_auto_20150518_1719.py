# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emailqueue', '0004_auto_20150518_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='mail',
            name='sleep_from',
            field=models.TimeField(default=None, help_text='Sleep From', null=True, verbose_name='Sleep From', blank=True),
        ),
        migrations.AddField(
            model_name='mail',
            name='sleep_to',
            field=models.TimeField(default=None, help_text='Sleep To', null=True, verbose_name='Sleep To', blank=True),
        ),
    ]
