# -*- coding: utf-8 -*-
'''

mail.cf:

- to eat all outbound message by "jail" transport

    ::

        default_transport=jail

maser.cf:

    ::

        jail unix  -   n    n   -   -   pipe
          flags=FDRq user=vagrant argv=/bin/inbound.sh $sender $recipient

Ubuntu:

- https://help.ubuntu.com/community/PostfixBasicSetupHowto

    ::

        sudo apt-get install postfix mailutils

'''

from pycommand.djcommand import Command, SubCommand
# from bs4 import BeautifulSoup as Soup

import sys
import logging
import traceback

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

            if sys.stdin.isatty():
                #: no stdin
                log.warn('no stdin')
                return

            iid = save_inbound(
                params.sender[0], params.recipient[0],
                ''.join(sys.stdin.read()))

            try:
                log.debug("bouncer.handle_main:process journal =%d" % iid)
                # process_journal.delay(jid)      #: defualt is async
            except:
                for err in traceback.format_exc().split('\n'):
                    log.error("bouncer.handle_main:%s" % err)

    class SendMessage(SubCommand):
        name = "send_messages"
        description = "bounce by incoming mail"
        args = [
        ]

        def run(self, params, **options):
            from emailsmtp.tasks import send_messages
            send_messages()
