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
                ('subject', models.TextField(help_text='Mail Subject Help', verbose_name='Mail Subject')),
                ('body', models.TextField(help_text='Mail Body Help', verbose_name='Mail Body')),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
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
            name='Outbound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('return_path', models.EmailField(help_text='Return Path Help', max_length=50, verbose_name='Return Path')),
                ('raw_message', models.TextField(default=None, help_text='Serialized Message Help', null=True, verbose_name='Serialized Message', blank=True)),
                ('due_at', models.DateTimeField(default=None, null=True, verbose_name='Due At', blank=True)),
                ('sent_at', models.DateTimeField(default=None, null=True, verbose_name='Sent At', blank=True)),
                ('mail', models.ForeignKey(default=None, to='emailqueue.Mail', blank=True, help_text='Mail Help', null=True, verbose_name='Mail')),
                ('recipient', models.ForeignKey(verbose_name='Recipient', to='emailqueue.MailAddress', help_text='Recipient Help')),
            ],
            options={
                'verbose_name': 'Outbound',
                'verbose_name_plural': 'Outbound',
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
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='Mail Service Name')),
                ('class_name', models.CharField(max_length=20, verbose_name='Mail Service Class Name')),
            ],
            options={
                'verbose_name': 'Mail Service',
                'verbose_name_plural': 'Mail Service',
            },
        ),
        migrations.AddField(
            model_name='outbound',
            name='service',
            field=models.ForeignKey(verbose_name='Service', to='emailqueue.Service', help_text='Service Help'),
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
