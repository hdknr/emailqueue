from __future__ import absolute_import
from celery import shared_task
from django.utils.timezone import now

from emailqueue import models

import logging
logger = logging.getLogger('emailqueue')


def get_mail_instance(mail):
    return isinstance(mail, models.Mail) and mail or \
        models.Mail.objects.get(id=mail)


def get_message_instance(message):
    return isinstance(message, models.Message) and message or \
        models.Message.objects.get(id=message)


def handle_mail(message, handler=None, domain=None, args=(), **kwargs):
    '''This message was bounced error :ref:`emailqueue.models.Mail`
    '''
    if len(args) > 1:
        # Bounced count up
        for ma in models.MailAddress.objects.filter(
            id=args[1], recipient__mail__id=args[0]
        ):
            ma.bounced = ma.bounced + 1
            ma.save()

    message.processed_at = now()
    message.save()


def handle_relay(message, **kwargs):
    '''Because the Message is error return mail to the Relay-ed message
    , so forward this message to original Relay.sender
    '''
    # Look for Relay
    relay = models.Relay.objects.filter(
        address=message.recipient).first()

    if relay:
        message.processed_at = now()
        message.forward_sender = message.forward_return_path
        message.forward_recipient = relay.sender
        message.save()

        message.server.handler.forward_message(message)


def handle_fwd(message, **kwargs):
    '''This message is an error mail to the forwarded error message.
    So, do nothing
    '''
    message.processed_at = now()
    message.save()


def handle_direct(message, **kwargs):
    '''Inbounce message is sent directly by a Sender

    :param Message message: :ref:`emailqueue.models.Message`

    - if recipient is defined as :ref:`emailqueue.models.Relay`,
      this Message is forwarded to `relay.address` .
    '''
    relay = models.Relay.objects.create_from_message(message)

    if relay and relay.postbox.forward:
        if not relay.postbox.forward.enabled:
            logger.warn(u"{0} is disabled.".format(
                relay.postbox.forward.__unicode__()))
        else:
            message.forward_sender = relay.address
            message.forward_recipient = relay.postbox.forward
            message.save()
            # Do Forwarding...
            message.server.handler.forward_message(message)

    # otherwise this Message is not handled
    # keep `processed_at` == None


def handle_default(message, **kwargs):
    '''Default handler

    - this message may be an error return
    '''
    message.processed_at = now()
    message.save()


@shared_task
def process_message(message):
    ''' Inbounde Message handler

    - call one of handler in ['direct', 'relay', 'fwd', 'mail', 'test', ]

    :param Message message: `emailqueue.models.Message` instance or `id`
    '''
    message = get_message_instance(message)
    params = message.bounced_parameters

    {'direct': handle_direct,       # Direct to server
     'relay': handle_relay,         # Error to Relayed
     'fwd': handle_fwd,             # Error to Forwarded Relayed Error
     'mail': handle_mail,           # Error to Mail(initiated this server)
     }.get(params['handler'],
           handle_default
           )(message=message, **params)


class Handler(object):
    '''Abstract Task Handler'''

    def send_mail(self, messaage, *args, **kwargs):
        '''Send Message

        :param Mail mail: :ref:`emailqueue.models.Mail`
        '''
        raise NotImplementedError

    def process_message(self, message, *args, **kwargs):
        process_message(message)

    def forward_message(self, message, *args, **kwargs):
        '''Forward Message

        :param Mail mail: :ref:`emailqueue.models.Mail`
        '''
        raise NotImplementedError
