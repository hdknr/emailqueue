# -*- coding: utf-8 -*-
'''

mail.cf(define transport for accepting domains):

    ::

        default_transport=jail

maser.cf(define transport handler script):

    ::

        jail unix  -   n    n   -   -   pipe
          flags=FDRq user=vagrant argv=/bin/inbound.sh $sender $recipient

inbound.sh(save to Message models):

    ::

        #!/bin/sh
        PY=/home/vagrant/.anyenv/envs/pyenv/versions/venv/bin/python
        MN=/home/vagrant/projects/emailqueue/web/manage.py

        $PY $MN empostfix bounce $1 $2

Ubuntu:

- https://help.ubuntu.com/community/PostfixBasicSetupHowto

    ::

        sudo apt-get install postfix mailutils

'''

from pycommand.djcommand import Command, SubCommand
# from bs4 import BeautifulSoup as Soup

import sys
import logging

from emailsmtp.tasks import save_inbound

log = logging.getLogger('emailsmtp')


class Command(Command):

    class Bounce(SubCommand):
        '''
            http://www.postfix.org/pipe.8.html
        '''

        name = "bounce"
        description = "bounce by incoming mail"
        args = [
            (('sender',), dict(nargs=1, help="Sender Address")),
            (('recipient',), dict(nargs=1, help="Recipient Address")),
        ]

        def run(self, params, **options):
            ''' read stdin and save it to `emailqueue.models.Message`
            '''

            if sys.stdin.isatty():
                #: no stdin
                log.warn('no stdin')
                return

            save_inbound(
                params.sender[0], params.recipient[0],
                ''.join(sys.stdin.read()))

    class SendMail(SubCommand):
        name = "send_mail"
        description = "Send messages of Mail"
        args = [
            (('id',), dict(nargs='*', help="Mail ID")),
        ]

        def run(self, params, **options):
            from emailsmtp.tasks import send_mail
            for id in params.id:
                send_mail(id)

    class SendMailTest(SubCommand):
        name = "send_mail_test"
        description = "Send test messages of Mail"
        args = [
            (('id',), dict(nargs=1, help="Mail ID")),
            (('recipients',), dict(nargs="*", help="Mail ID")),
        ]

        def run(self, params, **options):
            from emailsmtp.tasks import send_mail_test
            send_mail_test(params.id[0], params.recipients)
