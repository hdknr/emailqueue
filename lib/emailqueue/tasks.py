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


def forward_message(message, forwarder=None):
    ''' Forward message

    :param Message message: `emailqueue.models.Message`
    :param string forwarder: Celery forwarding task name

    '''
    forwarder = forwarder or (message.server and message.server.forwarder)

    if not forwarder:
        logger.error('no forwarder is given.')
        return

    from celery import current_app
    current_app.send_task(
        forwarder,
        args=[message.id, ])


def error_mail(message, prefix, domain, args, **kwargs):
    '''This message was error '''
    # TODO:
    message.processed_at = now()
    message.save()


def error_relay(message, handler, domain, args,
                forwarder=None, **kwargs):
    ''' Because the Message is error return mail to the Relay-ed message
        , so forward this message to Relay.sender
    '''
    relay = models.Relay.objects.filter(
        address=message.recipient).first()

    if relay:
        message.processed_at = now()
        message.forward_sender = message.forward_return_path
        message.forward_recipient = relay.sender.email
        message.save()

        forward_message(message, forwarder)


def error_test(message, prefix, domain, args, **kwargs):
    # TODO:
    message.processed_at = now()
    message.save()


def error_fwd(message, handler, domain, args, **kwargs):
    '''This message is an error mail to the forwarded error message.
    So, do nothing
    '''
    message.processed_at = now()
    message.save()


def process_direct(message, forwarder=None, **kwargs):
    '''Inbounce message is sent directly by a Sender

    :param Message message: :ref:`emailqueue.models.Message`

    - if recipient is defined as :ref:`emailqueue.models.Relay`,
      this Message is forwarded to `relay.address` .
    '''
    relay = models.Relay.objects.create_from_message(message)

    if relay:
        message.forward_sender = relay.address
        message.forward_recipient = relay.postbox.forward
        message.save()
        forward_message(message, forwarder)

    # TODO: check postbox for command execution


def handle_default(message, **kwargs):
    '''Default handler '''
    message.processed_at = now()
    message.save()


@shared_task
def process_message(message, forwarder=None):
    ''' Inbounde Message handler

    - call one of handler in ['direct', 'relay', 'fwd', 'mail', 'test', ]

    :param Message message: `emailqueue.models.Message` instance or `id`
    '''
    message = get_message_instance(message)
    params = message.get_handler()

    {'direct': process_direct,
     'relay': error_relay,
     'fwd': error_fwd,
     'mail': error_mail,
     'test': error_test,
     }.get(params['handler'], handle_default)(
        message=message, forwarder=forwarder, **params)
