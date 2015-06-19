# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import emailqueue.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('file', emailqueue.models.FileField(help_text='Attrachment File Help', upload_to=b'', verbose_name='Attachment File')),
            ],
            options={
                'verbose_name': 'Attachment',
                'verbose_name_plural': 'Attachment',
            },
        ),
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('name', models.CharField(default=None, max_length=50, blank=True, help_text='Mail Name Help', null=True, verbose_name='Mail Name')),
                ('subject', models.TextField(help_text='Mail Subject Help', verbose_name='Mail Subject')),
                ('body', models.TextField(help_text='Mail Body Help', verbose_name='Mail Body')),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('enabled', models.BooleanField(default=False, help_text='Enabled', verbose_name='Enabled')),
                ('due_at', models.DateTimeField(default=None, help_text='Due At', null=True, verbose_name='Due At', blank=True)),
                ('sleep_from', models.TimeField(default=None, help_text='Sleep From', null=True, verbose_name='Sleep From', blank=True)),
                ('sleep_to', models.TimeField(default=None, help_text='Sleep To', null=True, verbose_name='Sleep To', blank=True)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'verbose_name': 'Mail',
                'verbose_name_plural': 'Mail',
            },
        ),
        migrations.CreateModel(
            name='MailAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('email', models.EmailField(help_text='Email Address Help', max_length=50, verbose_name='Email Address')),
            ],
            options={
                'verbose_name': 'Mail Address',
                'verbose_name_plural': 'Mail Address',
            },
        ),
        migrations.CreateModel(
            name='MailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('name', models.CharField(help_text='Mail Name Help', unique=True, max_length=50, verbose_name='Mail Name', db_index=True)),
                ('subject', models.TextField(help_text='Mail Subject Help', verbose_name='Mail Subject')),
                ('body', models.TextField(help_text='Mail Body Help', verbose_name='Mail Body')),
            ],
            options={
                'verbose_name': 'Mail Template',
                'verbose_name_plural': 'Mail Template',
            },
        ),
        migrations.CreateModel(
            name='Postbox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('address', models.EmailField(help_text='Postbox Address Help', max_length=50, verbose_name='Postbox Address')),
                ('forward', models.EmailField(default=None, max_length=50, blank=True, help_text='Forwoard Address Help', null=True, verbose_name='Forwoard Address')),
                ('deleted', models.BooleanField(default=False, help_text='Is Deleted Help', verbose_name='Is Deleted')),
                ('task', models.TextField(default=None, help_text='Postbox Task Help', null=True, verbose_name='Postbox Task', blank=True)),
                ('blacklist', models.TextField(default=None, help_text='Black List Pattern Help', null=True, verbose_name='Black List Pattern', blank=True)),
            ],
            options={
                'verbose_name': 'Postbox',
                'verbose_name_plural': 'Postbox',
            },
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('return_path', models.EmailField(default=None, max_length=50, blank=True, help_text='Return Path Help', null=True, verbose_name='Return Path')),
                ('sent_at', models.DateTimeField(default=None, null=True, verbose_name='Sent At', blank=True)),
                ('mail', models.ForeignKey(verbose_name='Mail', to='emailqueue.Mail', help_text='Mail Help')),
                ('to', models.ForeignKey(verbose_name='Recipient Address', to='emailqueue.MailAddress', help_text='Recipient Address Help')),
            ],
            options={
                'verbose_name': 'Recipient',
                'verbose_name_plural': 'Recipient',
            },
        ),
        migrations.CreateModel(
            name='Relay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('sender', models.EmailField(help_text='Sender Address Help', max_length=50, verbose_name='Sender Address')),
                ('is_spammer', models.BooleanField(default=False, verbose_name='Is Spammer')),
                ('postbox', models.ForeignKey(verbose_name='Postbox', to='emailqueue.Postbox', help_text='Postbox Help')),
            ],
            options={
                'verbose_name': 'Relay',
                'verbose_name_plural': 'Relay',
            },
        ),
        migrations.AddField(
            model_name='mailtemplate',
            name='sender',
            field=models.ForeignKey(verbose_name='Mail Sender', to='emailqueue.Postbox', help_text='Mail Sender Help'),
        ),
        migrations.AddField(
            model_name='mail',
            name='sender',
            field=models.ForeignKey(verbose_name='Mail Sender', to='emailqueue.Postbox', help_text='Mail Sender Help'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='mail',
            field=models.ForeignKey(verbose_name='Mail', to='emailqueue.Mail', help_text='Mail Help'),
        ),
    ]
