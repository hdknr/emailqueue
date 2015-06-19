# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Inbound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('sender', models.CharField(help_text='Sender Help', max_length=100, verbose_name='Sender')),
                ('recipient', models.CharField(help_text='Recipient Help', max_length=100, verbose_name='Recipient')),
                ('raw_message', models.TextField(default=None, help_text='Raw Message Text Help', null=True, verbose_name='Raw Message Text', blank=True)),
                ('processed_at', models.DateTimeField(default=None, null=True, verbose_name='Processed At', blank=True)),
            ],
            options={
                'verbose_name': 'Inbound',
                'verbose_name_plural': 'Inbound',
            },
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='Mail Service Name')),
                ('domain', models.CharField(unique=True, max_length=50, verbose_name='Mail Domain Name')),
                ('backend', models.CharField(default=b'django.core.mail.backends.smtp.EmailBackend', max_length=100, verbose_name='Mail Backend')),
                ('wait_every', models.IntegerField(default=0, help_text='Wait sending for every count help', verbose_name='Wait sending for every count')),
                ('wait_ms', models.IntegerField(default=0, help_text='Wait milliseconds help', verbose_name='Wait milliseconds')),
            ],
            options={
                'verbose_name': 'SMTP Server',
                'verbose_name_plural': 'SMTP Server',
            },
        ),
    ]
