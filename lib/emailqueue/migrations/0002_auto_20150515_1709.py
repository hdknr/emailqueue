# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emailqueue', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mail',
            name='due_at',
            field=models.DateTimeField(default=None, help_text='Due At', null=True, verbose_name='Due At', blank=True),
        ),
        migrations.AddField(
            model_name='mail',
            name='enabled',
            field=models.BooleanField(default=False, help_text='Enabled', verbose_name='Enabled'),
        ),
        migrations.AddField(
            model_name='recipient',
            name='return_path',
            field=models.EmailField(default=None, max_length=50, blank=True, help_text='Return Path Help', null=True, verbose_name='Return Path'),
        ),
        migrations.AddField(
            model_name='recipient',
            name='sent_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='Sent At', blank=True),
        ),
    ]
