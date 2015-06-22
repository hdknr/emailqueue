''' Email Delivery Subsystem
'''
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.timezone import now
from django import template

import uuid
import os
from datetime import timedelta
from email import Charset,  message_from_string
from email.mime.text import MIMEText

import utils


class FileField(models.FileField):
    def get_internal_type(self):
        return 'FileField'

    def generate_filename(self, instance, filename):
        return os.path.join(
            u"{0}/{1}/{2}/{3}".format(
                instance._meta.db_table,
                str(instance.id),
                self.name,
                filename))


class BaseModel(models.Model):
    '''Base Model
    '''
    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )

    class Meta:
        abstract = True


class Postbox(BaseModel):
    ''' Mail Relay Definition
    '''
    address = models.EmailField(
        _('Postbox Address'), help_text=_('Postbox Address Help'),
        max_length=50)

    forward = models.EmailField(
        _('Forwoard Address'), help_text=_('Forwoard Address Help'),
        max_length=50, null=True, blank=True, default=None)

    deleted = models.BooleanField(
        _('Is Deleted'), help_text=_('Is Deleted Help'), default=False, )

    task = models.TextField(
        _('Postbox Task'), help_text=_('Postbox Task Help'),
        null=True, blank=True, default=None)

    blacklist = models.TextField(
        _('Black List Pattern'),
        help_text=_('Black List Pattern Help'),
        null=True, blank=True, default=None)

    class Meta:
        verbose_name = _('Postbox')
        verbose_name_plural = _('Postbox')

    def __unicode__(self):
        return u"{0} >> {1}".format(
            self.address, self.forward,
        )

    @property
    def domain(self):
        return self.address.split('@')[1]


class Relay(BaseModel):
    ''' Relay Entries for Postbox
    '''
    postbox = models.ForeignKey(
        Postbox,
        verbose_name=_('Postbox'), help_text=_('Postbox Help'))

    sender = models.EmailField(
        _('Sender Address'), help_text=_('Sender Address Help'), max_length=50)

    is_spammer = models.BooleanField(
        _('Is Spammer'), default=False)

    class Meta:
        verbose_name = _('Relay')
        verbose_name_plural = _('Relay')


class MailAddress(BaseModel):
    ''' Mail Address
    '''
    email = models.EmailField(
        _('Email Address'),
        help_text=_('Email Address Help'), max_length=50)

    bounced = models.IntegerField(
        _('Bounced Count'),
        help_text=_('Bounced Count Help'), default=0)

    class Meta:
        verbose_name = _('Mail Address')
        verbose_name_plural = _('Mail Address')

    def __unicode__(self):
        return self.email


class MailTemplate(BaseModel):
    sender = models.ForeignKey(
        Postbox,
        verbose_name=_('Mail Sender'), help_text=_('Mail Sender Help'))

    name = models.CharField(
        _('Mail Name'), help_text=_('Mail Name Help'),  max_length=50,
        unique=True, db_index=True)

    subject = models.TextField(
        _('Mail Subject'), help_text=_('Mail Subject Help'), )

    body = models.TextField(
        _('Mail Body'), help_text=_('Mail Body Help'), )

    class Meta:
        verbose_name = _('Mail Template')
        verbose_name_plural = _('Mail Template')


class MailQuerySet(models.QuerySet):
    def active_set(self, basetime=None):
        basetime = basetime or now()
        return self.filter(
            models.Q(due_at__isnull=True) | models.Q(due_at__lte=basetime),
            enabled=True,
        )

    def create_from_template(self, name, **kwargs):
        mt = MailTemplate.objects.get(name=name)
        return self.create(
            sender=mt.sender,
            name=mt.name,
            subject=mt.subject,
            body=mt.body,
            **kwargs
        )


class Mail(BaseModel):
    '''Mail Delivery Definition
    '''
    sender = models.ForeignKey(
        Postbox,
        verbose_name=_('Mail Sender'), help_text=_('Mail Sender Help'))

    name = models.CharField(
        _('Mail Name'), help_text=_('Mail Name Help'),  max_length=50,
        null=True, default=None, blank=True)

    subject = models.TextField(
        _('Mail Subject'), help_text=_('Mail Subject Help'), )

    body = models.TextField(
        _('Mail Body'), help_text=_('Mail Body Help'), )

    content_type = models.ForeignKey(
        ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    ctx = GenericForeignKey('content_type', 'object_id')

    enabled = models.BooleanField(
        _('Enabled'), help_text=_('Enabled'), default=False)

    due_at = models.DateTimeField(
        _('Due At'), help_text=_('Due At'),
        null=True, blank=True, default=None)

    sleep_from = models.TimeField(
        _('Sleep From'), help_text=_('Sleep From'),
        null=True, blank=True, default=None)

    sleep_to = models.TimeField(
        _('Sleep To'), help_text=_('Sleep To'),
        null=True, blank=True, default=None)

    class Meta:
        verbose_name = _('Mail')
        verbose_name_plural = _('Mail')

    objects = MailQuerySet.as_manager()

    def __unicode__(self):
        return self.subject

    def add_recipient(self, email):
        to, created = MailAddress.objects.get_or_create(email=email)
        recipient, created = Recipient.objects.get_or_create(
            mail=self, to=to,
            return_path=utils.to_return_path(
                prefix='eml', msg=self.id,
                to=to.id, domain=self.sender.domain))
        return recipient

    @property
    def subtype(self):
        # TODO: SHOULD BE configurable
        return 'plain'

    def is_active(self, dt=None):
        dt = dt or now()
        return self.enabled and (
            self.due_at is None or self.due_at <= dt)

    def update_due_at(self, days=0):
        self.due_at = now() + timedelta(days=days)

        # WARN:microsecond is trunctad by MySQL 5.6+
        self.due_at = self.due_at.replace(
            hour=self.sleep_to.hour,
            minute=self.sleep_to.minute,
            second=self.sleep_to.second,
            microsecond=self.sleep_to.microsecond,)
        self.save()

    def delay(self, dt=None):
        dd = now()
        dt = dt or dd.time()

        if any([
            not self.sleep_from, not self.sleep_to, not dt]
        ):
            return False

        if all([
            self.sleep_from <= self.sleep_to,
            self.sleep_from <= dt,
            dt <= self.sleep_to,
        ]):
            # MUST today
            self.update_due_at()
            return True

        if all([
            self.sleep_from > self.sleep_to,
        ]):

            if self.sleep_from <= dt:
                # Tommorrow
                self.update_due_at(1)
                return True

            elif dt <= self.sleep_to:
                # Today
                self.update_due_at()
                return True

        return False

    def rendered_message(self, mail_address):
        ''' MailAddress Object'''
        return template.Template(self.body).render(
            template.Context(dict(
                to=mail_address,
                ctx=self.ctx,
            )))

    def create_message(self, mail_address, encoding="utf-8",):
        ''' MailAddress Object'''

        # TODO: encoding depends on to.email doain actually
        message_id = uuid.uuid1().hex

        if encoding == 'utf-8':
            pass
        elif encoding == "shift_jis":
            #: DoCoMo
            #: TODO chekck message encoding and convert it
            Charset.add_charset(
                'shift_jis', Charset.QP, Charset.BASE64, 'shift_jis')
            Charset.add_codec('shift_jis', 'cp932')

        message = MIMEText(
            self.rendered_message(mail_address), self.subtype, encoding)

        message['Subject'] = self.subject
        message['From'] = self.sender.address
        message['To'] = mail_address.email
        message['Message-ID'] = message_id

        return message


class RecipientQuerySet(models.QuerySet):
    def active_set(self, basetime=None):
        basetime = basetime or now()
        return self.filter(
            models.Q(mail__due_at__isnull=True) |
            models.Q(mail__due_at__lte=basetime),
            mail__enabled=True,
            sent_at__isnull=True,
        )


class Recipient(BaseModel):
    '''Recipients for a Mail
    '''
    mail = models.ForeignKey(
        Mail, verbose_name=_('Mail'), help_text=_('Mail Help'))
    to = models.ForeignKey(
        MailAddress, verbose_name=_('Recipient Address'),
        help_text=_('Recipient Address Help'))

    return_path = models.EmailField(
        _('Return Path'), help_text=_('Return Path Help'), max_length=50,
        null=True, default=None, blank=True)
    sent_at = models.DateTimeField(
        _('Sent At'), null=True, blank=True, default=None)

    class Meta:
        verbose_name = _('Recipient')
        verbose_name_plural = _('Recipient')

    objects = RecipientQuerySet.as_manager()

    def create_message(self, encoding="utf-8",):
        return self.mail.create_message(self.to)


class Attachment(BaseModel):
    '''Attachemetns for a Mail
    '''
    mail = models.ForeignKey(
        Mail, verbose_name=_('Mail'), help_text=_('Mail Help'))

    file = FileField(
        _('Attachment File'),
        help_text=_('Attrachment File Help'),)

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachment')


class Message(BaseModel):
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
        verbose_name = _(u'Message')
        verbose_name_plural = _(u'Message')

    @property
    def mailobject(self):
        ''' return mail object

            :rtype: email.message.Message
        '''
        def _cached():
            # cache message_from_string(self.raw_message)
            self._mailobject = message_from_string(
                self.raw_message.encode('utf8'))
            return self._mailobject

        return getattr(self, '_mailobject', _cached())

    @property
    def is_multipart(self):
        return self.mailobject and self.mailobject.is_multipart() or False

    @property
    def dsn(self):
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

    def create_report(self):
        params = utils.from_return_path(self.recipient)
        if not params:
            return

        try:
            address = MailAddress.objects.get(id=params['to'])

            report, created = Report.objects.get_or_create(
                address=address, bounce=self,
                mail=Mail.objects.get(id=params['msg']))

            if created:
                address.bounced = address.bounced + 1
                address.save()
                report.action = self.dsn_action
                report.status = self.dsn_status
                report.save()
        except:
            pass


class Report(BaseModel):
    address = models.ForeignKey(
        MailAddress, verbose_name=_('Mail Address'),
        help_text=_('Mail Address Help'))

    mail = models.ForeignKey(
        Mail, verbose_name=_('Mail'),
        help_text=_('Mail Help'),
        null=True, blank=True, default=None, on_delete=models.SET_DEFAULT)

    bounce = models.ForeignKey(
        Message, verbose_name=_('Bounce Message'),
        help_text=_('Bounce Message Help'),
        null=True, blank=True, default=None, on_delete=models.SET_DEFAULT)

    action = models.CharField(
        _('DNS Action'), help_text=_('DSN Action Help'),  max_length=10,
        null=True, default=None, blank=True)

    status = models.CharField(
        _('DNS Status'), help_text=_('DSN Status Help'),  max_length=10,
        null=True, default=None, blank=True)

    class Meta:
        verbose_name = _(u'Report')
        verbose_name_plural = _(u'Report')
