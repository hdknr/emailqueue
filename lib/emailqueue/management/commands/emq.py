# -*- coding: utf-8 -*-

from pycommand.djcommand import Command as PyCommand, SubCommand
# from django.utils.translation import ugettext as _
from emailqueue import tasks, models
# import sys


class Command(PyCommand):
    managers = ['manage.py', ]

    class ProcessMessage(SubCommand):
        name = "process_message"
        description = "Process Message"
        args = [
            (('id',), dict(nargs=1, type=int, help="Message ID")),
        ]

        def run(self, params, **options):
            tasks.process_message(
                models.Message.objects.get(id=params.id[0]))

    class ActiveMailList(SubCommand):
        name = "list_active_mail"

        def run(self, params, **options):
            from emailqueue.models import Mail
            for mail in Mail.objects.active_set():
                print mail.id
