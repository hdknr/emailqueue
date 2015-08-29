from django.conf import settings
from django.core.mail import get_connection
from django.utils.timezone import now, get_current_timezone

# from celery import current_task
from celery.utils.log import get_task_logger
from celery.task import task
from celery import shared_task


import traceback

import models

from emailqueue import (
    models as queue_models,
    utils,
    tasks as queue_tasks,
)


logger = get_task_logger('emailsmtp')
BACKEND = getattr(settings, 'SMTP_EMAIL_BACKEND',
                  'django.core.mail.backends.smtp.EmailBackend')


def make_eta(when):
    ''' ETA(estimated time of arrival) time

        :param when:  :py:class:`datetime.datetime`
        :return: :py:class:`datetime.datetime` with timezone
    '''
    return when.tzinfo and when or get_current_timezone().localize(when)


def get_mail_instance(mail):
    ''' Find `emailqueue.models.Mail` instance

        :param mail:`emailqueue.models.Mail` instance or 'id' for instance
        :return: :ref:`emailqueue.models.Mail` instance
    '''
    return isinstance(mail, queue_models.Mail) and mail or \
        queue_models.Mail.objects.get(id=mail)


def get_message_instance(message):
    ''' Find `emailqueue.models.Message` instance

        :param mail:`emailqueue.models.Message` instance or 'id' for instance
        :return: :ref:`emailqueue.models.Message` instance
    '''
    return isinstance(message, queue_models.Message) and message or \
        queue_models.Message.objects.get(id=message)


@shared_task
def send_mail(mail):
    mail = get_mail_instance(mail)

    server = models.Server.objects.filter(
        domain=mail.sender.domain).first()

    if not server:
        logger.debug("No Server for {0}".format(mail.sender.domain))
        return

    logger.debug("Mail({0}) is sending {1} recipients".format(
        mail.id, mail.recipient_set.active_set()))

    for recipient in mail.recipient_set.active_set():
        if mail.delay():    # make this Mail pending state
            logger.info("Mail({0}) is delayed".format(mail.id))
            break

        send_raw_message(
            recipient.return_path,
            [recipient.to.email],
            recipient.create_message().as_string(),
            server.backend)

        recipient.sent_at = now()
        recipient.save()

        server.wait()


@shared_task
def send_mail_test(mail, recipients=None):
    ''' recipents : list of email address '''
    mail = get_mail_instance(mail)

    server = models.Server.objects.filter(
        domain=mail.sender.domain).first()

    if not server:
        logger.debug("No Server for {0}".format(mail.sender.domain))
        return

    recipients = recipients or [mail.sender.forward]

    for recipient in recipients:

        to = queue_models.MailAddress.objects.get_or_create(
            email=recipient)[0]

        return_path = utils.to_return_path(
            'test', mail.sender.domain, mail.id, to.id)

        send_raw_message(
            return_path,
            [recipient],
            mail.create_message(to).as_string(),
            server.backend)


@shared_task
def send_mail_all():
    for mail in queue_models.Mail.objects.active_set():
        send_mail(mail)


@shared_task
def send_raw_message(
        return_path, recipients,
        raw_message, *args, **kwargs):
    '''
        :param str return_path: the Envelope From address
        :param list(str) recipients: the Envelope To address
        :param str raw_message:
            string expression of Python email.message.Message object
    '''

    # logger = current_task.get_logger()
    try:
        conn = get_connection(backend=BACKEND)
        conn.open()     # django.core.mail.backends.smtp.EmailBackend
        conn.connection.sendmail(
            return_path, recipients, raw_message)

        logger.debug(
            "send_email_in_string:Successfully sent email message to %r.",
            recipients)

    except Exception, e:
        # catching all exceptions b/c it could be any number of things
        # depending on the backend
        logger.debug(traceback.format_exc())
        logger.warning(
            "{0}:Failed to send email message to {1}, retrying.".format(
                'send_email_instring', recipients))
        send_raw_message.retry(exc=e)


@task
def save_inbound(sender, recipient, raw_message):
    '''
    Save `raw_message`(serialized email) to
    `emailqueue.models.Message`

        :param sender: sender email address
        :param recipient: recipient email address
        :param raw_message: seriazlied email text
    '''
    inbound = queue_models.Message.objects.create(
        sender=sender, recipient=recipient, raw_message=raw_message)

    queue_tasks.process_message(
        inbound, forwarder='emailsmtp.tasks.forward')


@shared_task
def forward(message):
    ''' queue_models.Message '''

    message = get_message_instance(message)
    server = models.Server.objects.filter(
        domain=message.forward_sender.split('@')[1]).first()

    send_raw_message(
        message.forward_sender,
        [message.forward_recipient],
        message.raw_message,
        server.backend)

    message.processed_at = now()
    message.save()
