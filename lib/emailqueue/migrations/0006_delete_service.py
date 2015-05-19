# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emailsmtp', '0002_auto_20150519_1025'),
        ('emailqueue', '0005_auto_20150518_1719'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Service',
        ),
    ]
