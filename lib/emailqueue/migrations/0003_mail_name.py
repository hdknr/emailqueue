# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emailqueue', '0002_auto_20150515_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='mail',
            name='name',
            field=models.CharField(default=None, max_length=50, blank=True, help_text='Mail Name Help', null=True, verbose_name='Mail Name'),
        ),
    ]
