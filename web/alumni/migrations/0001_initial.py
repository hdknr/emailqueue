# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('family_name', models.CharField(max_length=50, verbose_name='Family Name')),
                ('first_name', models.CharField(max_length=50, verbose_name='First Name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
