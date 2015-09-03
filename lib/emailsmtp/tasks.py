''' Tasks for emailsmtp
'''

from django.conf import settings
from django.core.mail import get_connection
from django.utils.timezone import now, get_current_timezone
from django.utils.encoding import smart_str
from django.core.mail.backends.smtp import EmailBackend

# from celery import current_task
from celery import shared_task


import traceback

from emailqueue import (
    models as queue_models,
    tasks as queue_tasks,
    utils,
)

import logging
logger = logging.getLogger('emailsmtp')

BACKEND = getattr(settings, 'SMTP_EMAIL_BACKEND', settings.EMAIL_BACKEND)


def make_eta(when):
    '''ETA(estimated time of arrival) time

        :param when:  :py:class:`datetime.datetime`
        :return: :py:class:`datetime.datetime` with timezone
    '''
    if when:
        return when.tzinfo and when or get_current_timezone().localize(when)
    else:
        return when


def get_mail_instance(mail):
    ''' Find `emailqueue.models.Mail` instance

    :param mail: :ref:`emailqueue.models.Mail` instance
                  or 'id' for instance
    :return: :ref:`emailqueue.models.Mail` instance
    '''
    return isinstance(mail, queue_models.Mail) and mail or \
        queue_models.Mail.objects.get(id=mail)


def get_message_instance(message):
    ''' Find `emailqueue.models.Message` instance

        :param mail: :ref:`emailqueue.models.Message` instance
                     or 'id' for instance
        :return: :ref:`emailqueue.models.Message` instance
    '''
    return isinstance(message, queue_models.Message) and message or \
        queue_models.Message.objects.get(id=message)


@shared_task
def send_mail(mail, recipients=None):
    '''Send mail

    :param Mail mail:  :ref:`emailqueue.models.Mail` or id
    :param list(Email) recipients: List of adhoc recipients.

    If `recipients` is not specified,
    :ref:`emailqueue.models.Recipient` list is used.
    '''
    mail = get_mail_instance(mail)

    server = mail.sender.server
    if not server:
        logger.debug("No Server for {0}".format(mail.sender.domain))
        return

    if mail.sent_at:
        # Already completed
        logger.warn("This message has been already processed")
        return

    # active_set:
    #   - recipients already sent (sent_at is not None)are NOT included
    recipients = recipients or mail.recipient_set.active_set()

    for recipient in recipients:
        if mail.delay():    # make this Mail pending state
            logger.info("Mail({0}) is delayed".format(mail.id))
            # enqueue another task
            send_mail.apply_async(
                args=[mail.id, None],           # TODO: in the case of adhoc
                eta=make_eta(mail.due_at))
            # terminate this task
            return

        if isinstance(recipient, basestring):
            to = queue_models.MailAddress.objects.get_or_create(
                email=recipient)[0]
            return_path = utils.to_return_path(
                'adhoc', mail.sender.domain, mail.id, to.id)
        else:
            to = recipient.to
            return_path = recipient.return_path

        if not to.enabled:
            logger.warn(u"{0} is disabled".format(to.__unicode__()))
            continue

        send_raw_message(
            return_path,
            [to.email],
            mail.create_message(to).as_string(),
            server.backend)

        if isinstance(recipient, queue_models.Recipient):
            recipient.sent_at = now()
            recipient.save()

        server.wait()

    # completed sending
    mail.sent_at = now()
    mail.save()


@shared_task
def send_raw_message(
        return_path, recipients,
        raw_message, *args, **kwargs):
    '''
    Send email using SMTP backend

    :param str return_path: the Envelope From address
    :param list(str) recipients: the Envelope To address
    :param str raw_message:
        string expression of Python :py:class:`email.message.Message` object
    '''

    try:
        conn = get_connection(backend=BACKEND)
        if conn and isinstance(conn, EmailBackend):
            conn.open()     # django.core.mail.backends.smtp.EmailBackend
            conn.connection.sendmail(
                return_path, recipients, smart_str(raw_message))
        else:
            store_raw_message(
                return_path, recipients, raw_message, *args, **kwargs)

    except Exception, e:
        # catching all exceptions b/c it could be any number of things
        # depending on the backend
        logger.debug(traceback.format_exc())
        logger.warning(
            "{0}:Failed to send email message to {1}, retrying.".format(
                'send_email_instring', recipients))
        send_raw_message.retry(exc=e)


@shared_task
def store_raw_message(
        return_path, recipients,
        raw_message, *args, **kwargs):
    '''
    Store email to :ref:`emailqueue.models.Message` for DEBUG

    :param str return_path: the Envelope From address
    :param list(str) recipients: the Envelope To address
    :param str raw_message:
        string expression of Python :py:class:`email.message.Message` object
    '''
    for recipient in recipients:
        user, domain = recipient.split('@')
        try:
            server = queue_models.Server.objects.filter(domain=domain).first()
            queue_models.Message.objects.create(
                server=server,
                sender=return_path,
                recipient=recipient,
                raw_message=raw_message)
        except:
            logger.debug(traceback.format_exc())


@shared_task
def save_inbound(sender, recipient, raw_message):
    '''
    Save `raw_message` (serialized email) to  :ref:`emailqueue.models.Message`
    This is called by bounce hander defined in SMTP server
    (ex. transport defined in Postfix :ref:`master.cf`).

    1. Create a new `emailqueue.models.Message`.
    2. Give it to `emailqueue.tasks.process_message` task.

    :param email sender: sender address
    :param email recipient: recipient address
    :param basestring raw_message: seriazlied email
    '''

    try:
        server = queue_models.Server.objects.filter(
            domain=recipient.split('@')[1]).first()
        inbound = queue_models.Message.objects.create(
            server=server,
            sender=sender, recipient=recipient, raw_message=raw_message)

        queue_tasks.process_message(inbound)
    except:
        logger.error(traceback.format_exc())


@shared_task
def forward(message):
    '''
    Forward to inboud mail to out side.

    :param Message message: :ref:`emailqueue.models.Message`
    '''
    assert message.forward_recipient, "Forward Reipient MUST be specified."

    message = get_message_instance(message)
    server = queue_models.Server.objects.filter(
        domain=message.forward_sender.split('@')[1]).first()

    send_raw_message(
        message.forward_sender,
        [message.forward_recipient.email],
        message.raw_message,
        server.backend)

    message.processed_at = now()
    message.save()


# @shared_task
# def send_mail_all():
#     for mail in queue_models.Mail.objects.active_set():
#         send_mail(mail)


class Handler(queue_tasks.Handler):
    '''SMTP Handler)
    '''
    def send_mail(self, mail, recipients=None, due_at=None, *args, **kwargs):
        '''SMTP: send  Mail

        :param Mail mail: :ref:`emailqueue.models.Mail` instance
        :param list(address) recipients: adhoc recipients or None

        If `recipients` is None, :ref:`emailqueue.models.Recipient`
        of this Mail are used.
        '''
        send_mail.apply_async(
            args=[mail.id, recipients],
            eta=make_eta(due_at or mail.due_at))

    def forward_message(self, message):
        '''SMTP:Forward a Message
        :param Mail mail: :ref:`emailqueue.models.Mail` instance
        '''
        forward(message)
