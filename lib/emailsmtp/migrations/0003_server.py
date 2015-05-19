# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emailsmtp', '0002_auto_20150519_1025'),
    ]

    operations = [
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='Mail Service Name')),
                ('domain', models.CharField(unique=True, max_length=50, verbose_name='Mail Domain Name')),
                ('backend', models.CharField(default=b'django.core.mail.backends.smtp.EmailBackend', max_length=100, verbose_name='Mail Backend')),
            ],
            options={
                'verbose_name': 'SMTP Server',
                'verbose_name_plural': 'SMTP Server',
            },
        ),
    ]
