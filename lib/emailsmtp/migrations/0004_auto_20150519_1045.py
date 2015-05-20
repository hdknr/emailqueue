# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emailsmtp', '0003_server'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='wait_every',
            field=models.IntegerField(default=0, help_text='Wait sending for every count help', verbose_name='Wait sending for every count'),
        ),
        migrations.AddField(
            model_name='server',
            name='wait_ms',
            field=models.IntegerField(default=0, help_text='Wait milliseconds help', verbose_name='Wait milliseconds'),
        ),
    ]
