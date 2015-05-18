# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emailqueue', '0001_initial'),
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
            name='SmtpServer',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='emailqueue.Service')),
            ],
            options={
                'verbose_name': 'SMTP Server',
                'verbose_name_plural': 'SMTP Server',
            },
            bases=('emailqueue.service',),
        ),
    ]
