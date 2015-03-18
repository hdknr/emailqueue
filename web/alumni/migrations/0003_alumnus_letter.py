# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emailqueue', '0007_auto_20150319_0127'),
        ('alumni', '0002_auto_20150319_0137'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alumnus',
            fields=[
                ('profile_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='alumni.Profile')),
                ('entered_year', models.IntegerField(verbose_name='Entered Year')),
                ('entered_school', models.CharField(max_length=50, verbose_name='Entered School')),
                ('graduated_year', models.IntegerField(verbose_name='Graduated Year')),
                ('graduated_school', models.CharField(max_length=50, verbose_name='Graduated School')),
            ],
            options={
                'abstract': False,
            },
            bases=('alumni.profile',),
        ),
        migrations.CreateModel(
            name='Letter',
            fields=[
                ('mail_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='emailqueue.Mail')),
            ],
            options={
                'abstract': False,
            },
            bases=('emailqueue.mail',),
        ),
    ]
