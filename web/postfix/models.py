from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from django.core import serializers

from email import message_from_string


class BaseModel(models.Model):
    '''Base Model
    '''
    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )

    class Meta:
        abstract = True

    def to_fixture(self):
        return serializers.serialize(
            "json", [self], ensure_ascii=False, indent=4)


class Domain(BaseModel):
    domain = models.CharField(
        _('Domain'), max_length=50, unique=True, db_index=True,)
    transport = models.CharField(
        _('Transport'), max_length=200)
    alias_domain = models.ForeignKey(
        'Domain', verbose_name=_('Alias Transport'),
        related_name='alias_domain_set',
        null=True, default=None, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _('Domain')
        verbose_name_plural = _('Domain')

    def __unicode__(self):
        return self.domain

    def create_alias_domain(self, name):
        domain, created = Domain.objects.get_or_create(
            doamin=name, transport='error',
            alias=self)
        return domain

    def add_alias_address(self, user, alias_user=None):
        src = '{0}@{1}'.format(user, self.domain)
        dst = '{0}@{1}'.format(alias_user or user, self.alias_domain.domain)
        alias = self.alias_set.filter(recipient=src).first()
        if alias:
            alias.forward = dst
            alias.save()
        else:
            alias = self.alias_set.create(recipient=src, forward=dst)
        return alias


class Alias(BaseModel):
    domain = models.ForeignKey(
        Domain,
        null=True, default=None, blank=True, on_delete=models.SET_NULL)

    recipient = models.EmailField(
        _('Recipient Address'), max_length=100, unique=True, db_index=True)

    forward = models.EmailField(
        _('Forward Address'), max_length=100)

    class Meta:
        verbose_name = _('Alias')
        verbose_name_plural = _('Alias')

    def __unicode__(self):
        return u"{0}>{1}".format(self.recipient, self.forward)


class MailMessage(BaseModel):
    raw_message = models.TextField(
        _(u'Raw Message Text'), help_text=_(u'Raw Message Text Help'),
        default=None, blank=True, null=True)

    class Meta:
        abstract = True

    def load_message(self, path):
        '''Load Raw Message '''
        self._mailobject = None     # clear cache
        with open(path) as src:
            self.raw_message = src.read()

    @property
    def mailobject(self):
        ''' return mail object

        :rtype: email.message.Message
        '''
        def _cached():
            # cache message_from_string(self.raw_message)
            self._mailobject = message_from_string(
                smart_str(self.raw_message))

            # self.raw_message.encode('utf8'))
            return self._mailobject

        return getattr(self, '_mailobject', _cached())

    @property
    def is_multipart(self):
        return self.mailobject and self.mailobject.is_multipart() or False

    @property
    def dsn(self):
        ''' DSN object if a Message has something wrong. '''
        def _cached():
            if self.is_multipart and isinstance(
                    self.mailobject.get_payload(), list):
                # cache dns
                self._dsn = self.mailobject.get_payload(1)
                return self._dsn
            return None

        return getattr(self, '_dsn', _cached())

    @property
    def dsn_action(self):
        try:
            return self.dsn and self.dsn.get_payload(1)['action']
        except:
            return None

    @property
    def dsn_status(self):
        try:
            return self.dsn and self.dsn.get_payload(1)['status']
        except:
            return None


class Message(MailMessage):
    ''' Raw Message '''

    sender = models.EmailField(
        _('Sender'), help_text=_('Sender Help'),  max_length=100,
        default=None, blank=True, null=True)

    recipient = models.EmailField(
        _('Recipient'), help_text=_('Recipient Help'), max_length=100,
        default=None, blank=True, null=True)

    processed_at = models.DateTimeField(
        _('Processed At'), null=True, blank=True, default=None)

    class Meta:
        verbose_name = _(u'Message')
        verbose_name_plural = _(u'Message')
