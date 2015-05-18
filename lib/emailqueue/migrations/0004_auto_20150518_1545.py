# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emailqueue', '0003_mail_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outbound',
            name='mail',
        ),
        migrations.RemoveField(
            model_name='outbound',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='outbound',
            name='service',
        ),
        migrations.DeleteModel(
            name='Outbound',
        ),
    ]
