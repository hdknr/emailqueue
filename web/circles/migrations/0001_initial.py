# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alumni', '0001_initial'),
        ('emailqueue', '0004_attachment_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='Circle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Circle Name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CircleLetter',
            fields=[
                ('mail_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='emailqueue.Mail')),
                ('circle', models.ForeignKey(to='circles.Circle')),
            ],
            options={
                'abstract': False,
            },
            bases=('emailqueue.mail',),
        ),
        migrations.CreateModel(
            name='CircleMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alumnus', models.ForeignKey(to='alumni.Alumnus')),
                ('circle', models.ForeignKey(to='circles.Circle')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
