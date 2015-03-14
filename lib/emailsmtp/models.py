from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible

from email import message_from_string

from emailqueue.models import BaseModel, Service


class SmtpServer(Service):
    class Meta:
        verbose_name = _('SMTP Server')
        verbose_name_plural = _('SMTP Server')

    def save(self, *args, **kwargs):
        self.class_name = 'smtpserver'
        super(SmtpServer, self).save(*args, **kwargs)

    def send(self, outbound):
        import tasks
        tasks.send_raw_message(
            outbound.return_path,
            [outbound.recipient.email],
            outbound.raw_message,
        )


@deconstructible
class Inbound(BaseModel):
    ''' Raw Message '''

    sender = models.CharField(
        _('Sender'), help_text=_('Sender Help'),  max_length=100)

    recipient = models.CharField(
        _('Recipient'), help_text=_('Recipient Help'), max_length=100)

    raw_message = models.TextField(
        _(u'Raw Message Text'), help_text=_(u'Raw Message Text Help'),
        default=None, blank=True, null=True)

    class Meta:
        verbose_name = _(u'Inbound')
        verbose_name_plural = _(u'Inbound')

    def mailobject(self):
        ''' return mail object

            :rtype: email.message.Message
        '''
        return message_from_string(self.raw_message)
