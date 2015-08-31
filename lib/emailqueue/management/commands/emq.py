# -*- coding: utf-8 -*-

from pycommand.djcommand import Command as PyCommand, SubCommand
# from django.utils.translation import ugettext as _
from emailqueue import models
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
            for message in models.Message.objects.filter(id__in=params.id):
                message.server.handler.process_message(message)

    class SendMail(SubCommand):
        name = "send_mail"
        description = "Send Mail"
        args = [
            (('id',), dict(nargs=1, type=int, help="Mail ID")),
            (('recipients',), dict(nargs='*', help="Recipients")),
        ]

        def run(self, params, **options):
            mail = models.Mail.objects.get(id=params.id[0])
            mail.sender.server.handler.send_mail(
                mail, recipients=params.recipients)

    class ActiveMailList(SubCommand):
        name = "list_active_mail"

        def run(self, params, **options):
            from emailqueue.models import Mail
            for mail in Mail.objects.active_set():
                print mail.id
