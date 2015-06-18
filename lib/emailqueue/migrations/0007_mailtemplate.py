# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emailqueue', '0006_delete_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('name', models.CharField(help_text='Mail Name Help', unique=True, max_length=50, verbose_name='Mail Name', db_index=True)),
                ('subject', models.TextField(help_text='Mail Subject Help', verbose_name='Mail Subject')),
                ('body', models.TextField(help_text='Mail Body Help', verbose_name='Mail Body')),
                ('sender', models.ForeignKey(verbose_name='Mail Sender', to='emailqueue.Postbox', help_text='Mail Sender Help')),
            ],
            options={
                'verbose_name': 'Mail Template',
                'verbose_name_plural': 'Mail Template',
            },
        ),
    ]
