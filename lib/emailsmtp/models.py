from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible

from email import message_from_string

from emailqueue.models import BaseModel


class Server(BaseModel):
    name = models.CharField(
        _('Mail Service Name'), unique=True, max_length=50)

    domain = models.CharField(
        _('Mail Domain Name'), unique=True, max_length=50)

    backend = models.CharField(
        _('Mail Backend'), max_length=100,
        default='django.core.mail.backends.smtp.EmailBackend',)

    class Meta:
        verbose_name = _('SMTP Server')
        verbose_name_plural = _('SMTP Server')


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

    processed_at = models.DateTimeField(
        _('Processed At'), null=True, blank=True, default=None)

    class Meta:
        verbose_name = _(u'Inbound')
        verbose_name_plural = _(u'Inbound')

    def mailobject(self):
        ''' return mail object

            :rtype: email.message.Message
        '''
        return message_from_string(self.raw_message)
