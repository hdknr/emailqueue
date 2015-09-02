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

    class RawMessage(SubCommand):
        name = "raw_message"
        description = "Raw Message"
        args = [
            (('path',), dict(nargs='*', help="Path to Email Messsae File ")),
        ]

        def get_dsn(self, message):
            if message.is_multipart() and isinstance(
                    message.get_payload(), list):
                return message.get_payload(1)
            return None

        def run(self, params, **options):
            '''
            - http://docs.python.jp/2/library/email.message.html
            '''
            from email import message_from_string
            from email.message import Message
            from email.utils import parseaddr
            for path in params.path:
                with open(path) as data:
                    msg = message_from_string(data.read())
                    assert isinstance(msg, Message)
                    print "* ", path
                    print "  From:", parseaddr(msg['From'])[1]
                    print "  Mime:", msg['MIME-Version']

                    key = 'X-Failed-Recipients'
                    print key, ":", msg[key]

                    # print dir(msg)
                    print "Multipart? : ", msg.is_multipart()
                    for part in msg.walk():
                        print "@@@", part.get_content_type()
