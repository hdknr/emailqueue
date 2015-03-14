from django.conf import settings
from django.core.mail import get_connection

from celery import current_task
from celery.utils.log import get_task_logger
from celery.task import task

import traceback

import models


logger = get_task_logger('emailsmtp')
BACKEND = getattr(settings, 'SMTP_EMAIL_BACKEND',
                  'django.core.mail.backends.smtp.EmailBackend')


@task
def send_raw_message(
        return_path, recipients,
        raw_message, *args, **kwargs):
    '''
        :param str return_path: the Envelope From address
        :param list(str) recipients: the Envelope To address
        :param str raw_message:
            string expression of Python email.message.Message object
    '''

    logger = current_task.get_logger()
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
    inbound = models.Inbound(
        sender=sender, recipient=recipient,
        raw_message=raw_message)
    inbound.save()
    return inbound.id
