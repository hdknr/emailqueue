''' Tasks for emailsmtp
'''

from django.conf import settings
from django.core.mail import get_connection
from django.utils.timezone import now, get_current_timezone
from django.utils.encoding import smart_str
from django.core.mail.backends.smtp import EmailBackend

# from celery import current_task
from celery import shared_task
from celery.utils.log import get_task_logger

from datetime import timedelta
import traceback

from emailqueue import (
    models as queue_models,
    tasks as queue_tasks,
)

logger = get_task_logger(__name__)

BACKEND = getattr(settings, 'SMTP_EMAIL_BACKEND', settings.EMAIL_BACKEND)


def make_eta(when=None):
    '''ETA(estimated time of arrival) time

        :param when:  :py:class:`datetime.datetime`
        :return: :py:class:`datetime.datetime` with timezone
    '''
    when = when or now()
    return when.tzinfo and when or get_current_timezone().localize(when)


def get_mail_instance(mail):
    ''' Find `emailqueue.models.Mail` instance

    :param mail: :ref:`emailqueue.models.Mail` instance
                  or 'id' for instance
    :return: :ref:`emailqueue.models.Mail` instance
    '''
    return isinstance(mail, queue_models.Mail) and \
        queue_models.Mail.objects.get(id=mail.id) or \
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
    # mail.refresh_from_db()

    server = mail.sender.server
    if not server:
        logger.debug("No Server for {0}".format(mail.sender.domain))
        return

    if mail.sent_at or mail.status == mail.STATUS_DISABLED:
        # Already completed
        logger.warn(u"{0} {1} {2} {3}".format(
            u"This message has been already processed",
            mail.sent_at, mail.status, mail.subject,
        ))
        return

    # BEGIN:
    if mail.status != mail.STATUS_SENDING:
        mail.status = mail.STATUS_SENDING
        mail.save()         # post_save signle fires again

    # active_set:
    #   - recipients already sent (sent_at is not None)are NOT included
    recipients = recipients or mail.recipient_set.active_set()

    for recipient in recipients:

        # INTERUPTED:
        if mail.delay():    # make this Mail pending state
            logger.info("Mail({0}) is delayed".format(mail.id))
            # enqueue another task
            send_mail.apply_async(
                args=[mail.id, None],           # TODO: in the case of adhoc
                eta=make_eta(mail.due_at))
            # terminate this task
            return

        return_path, to = mail.get_return_path_and_to(recipient)

        if not return_path and not to:
            logger.warn(u"recipient({0}) is not valid".format(recipient))
            continue

        if not to.enabled:
            logger.warn(u"{0} is disabled".format(to.__unicode__()))
            continue

        mail.refresh_from_db()
        if mail.status != mail.STATUS_SENDING:
            logger.warn(u"Sending Mail({0}) has been interrupted".format(
                mail.id))
            return

        send_raw_message(
            return_path,
            [to.email],
            mail.create_message(to).as_string(),
            server.backend)

        if isinstance(recipient, queue_models.Recipient):
            recipient.sent_at = now()
            recipient.save()

        server.wait()

    # END: completed sending
    mail.status = mail.STATUS_SENT
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

    except:
        # catching all exceptions b/c it could be any number of things
        # depending on the backend
        logger.debug(traceback.format_exc())
        logger.warning(
            "{0}:Failed to send email message to {1}, retrying.".format(
                'send_email_instring', recipients))
        # send_raw_message.retry(exc=e)


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
                service='debug',
                sender=return_path,
                recipient=recipient,
                original_recipient=recipient,
                raw_message=raw_message)
        except:
            logger.debug(traceback.format_exc())


@shared_task
def save_inbound(service, sender, recipient, original_recipient,
                 raw_message, *args, **kwargs):
    '''
    Save `raw_message` (serialized email) to  :ref:`emailqueue.models.Message`
    This is called by bounce hander defined in SMTP server
    (ex. transport defined in Postfix :ref:`master.cf`).

    1. Create a new `emailqueue.models.Message`.
    2. Give it to `emailqueue.tasks.process_message` task.

    :param string service: service name
    :param email sender: sender address
    :param email recipient: recipient address
    :param email original_recipient: origninal recipient address
    :param basestring raw_message: seriazlied email
    '''

    try:
        server = queue_models.Server.objects.filter(
            domain=recipient.split('@')[1]).first()
        inbound = queue_models.Message.objects.create(
            server=server,
            service=service,
            sender=sender,
            recipient=recipient,
            original_recipient=original_recipient,
            raw_message=raw_message, )

        inbound.process_message()
    except:
        logger.error(traceback.format_exc())


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

        eta = make_eta(due_at or mail.due_at) + timedelta(seconds=1)
        # WARNING:
        #   timedelta to wait the transaction for `mail` will be commited

        send_mail.apply_async(args=[mail.id, recipients], eta=eta)

    def relay_message(self, message):
        send_raw_message(message.relay_return_path,
                         [message.relay_to],
                         message.raw_message)
        message.processed_at = now()
        message.save()

    def reverse_message(self, message):
        send_raw_message(message.reverse_return_path,
                         [message.reverse_to],
                         message.raw_message)
        message.processed_at = now()
        message.save()
