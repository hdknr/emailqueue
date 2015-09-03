''' Email Delivery Subsystem
'''
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now, localtime
# from django.utils.encoding import force_text
from django.utils.encoding import smart_str
from django import template
from django.core import serializers

import pydoc
import uuid
import os
from datetime import timedelta
from email import Charset,  message_from_string
from email.mime.text import MIMEText
import time

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

    def to_fixture(self):
        return serializers.serialize(
            "json", [self], ensure_ascii=False, indent=4)


class Server(BaseModel):
    name = models.CharField(
        _('Mail Service Name'), unique=True, max_length=50)

    domain = models.CharField(
        _('Mail Domain Name'), unique=True, max_length=50)

    backend = models.CharField(
        _('Mail Backend'), max_length=100,
        default='django.core.mail.backends.smtp.EmailBackend',)

    handler_class = models.CharField(
        _('Service Handler'), max_length=200,
        default='emailsmtp.tasks.Handler',)

    settings = models.TextField(
        _('Mail Server Settings'), null=True, default='{}', blank=True)

    wait_every = models.IntegerField(
        _('Wait sending for every count'),
        help_text=_('Wait sending for every count help'),
        default=0)

    wait_ms = models.IntegerField(
        _('Wait milliseconds'),
        help_text=_('Wait milliseconds help'),
        default=0)

    class Meta:
        verbose_name = _('Server')
        verbose_name_plural = _('Server')

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self._every = 0

    def __unicode__(self):
        return self.name

    def wait(self):
        self._every = self._every + 1
        if self.wait_every < self._every:
            self._every = 0
            if self.wait_every > 0:
                time.sleep(self.wait_ms / 1000.0)

    @property
    def handler(self):
        def create_handler():
            self._handler = pydoc.locate(self.handler_class)()
        return getattr(self, '_handler', create_handler())


class MailAddress(BaseModel):
    ''' Mail Address
    '''
    email = models.EmailField(
        _('Email Address'),
        help_text=_('Email Address Help'), max_length=50)

    bounced = models.IntegerField(
        _('Bounced Count'),
        help_text=_('Bounced Count Help'), default=0)

    enabled = models.BooleanField(
        _('Enabled Address'), help_text=_('Enabled Address Help'),
        default=True)

    class Meta:
        verbose_name = _('Mail Address')
        verbose_name_plural = _('Mail Address')

    def __unicode__(self):
        return self.email

    @property
    def domain(self):
        def _cached():
            self._domain = self.email and self.email.split('@')[1] or None
            return self._domain

        return getattr(self, '_domain', _cached())


class Postbox(BaseModel):
    ''' Mail Forwarding Definition
    '''
    server = models.ForeignKey(
        Server, verbose_name=_('Sending Server'),)

    address = models.EmailField(
        _('Postbox Address'), help_text=_('Postbox Address Help'),
        max_length=50)

    forward = models.ForeignKey(
        MailAddress, verbose_name=_('Forward Address'),
        help_text=_('Forward Address Help'),
        null=True, blank=True, default=None, on_delete=models.SET_DEFAULT)

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
        to = self.forward and self.forward.email or ''
        return u"{0} >> {1}".format(self.address, to,)

    @property
    def domain(self):
        return self.server.domain


class RelayQuerySet(models.QuerySet):
    def create_from_message(self, message):
        '''Create a Relay for Message '''

        postbox = Postbox.objects.filter(address=message.recipient).first()
        if not postbox:
            return None

        # TODO Postbox.blacklist filter

        sender, created = MailAddress.objects.get_or_create(
            email=message.sender)

        # return-path
        address = utils.to_return_path(
            "relay", postbox.domain,
            sender.id, postbox.id,)

        relay, created = self.get_or_create(
            address=address,
            postbox=postbox, sender=sender)

        return relay


class Relay(BaseModel):
    ''' Relay Entries for Postbox
    '''
    address = models.EmailField(
        _('Relay Return-Path Address'),
        help_text=_('Relay Return-Path Address Help'),
        max_length=50, db_index=True, unique=True)

    sender = models.ForeignKey(
        MailAddress,
        verbose_name=_('Original Sender Address'),
        help_text=_('Original Sender Address Help'))

    postbox = models.ForeignKey(
        Postbox,
        verbose_name=_('Original Recipient Postbox'),
        help_text=_('Original Recipient Postbox Help'))

    is_spammer = models.BooleanField(
        _('Is Spammer'), default=False)

    class Meta:
        verbose_name = _('Relay')
        verbose_name_plural = _('Relay')

    objects = RelayQuerySet.as_manager()


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

    ctx = models.TextField(
        _('Context Data'), help_text=_('Context Data Help'),
        default=None, null=True, blank=True)

    due_at = models.DateTimeField(
        _('Due At'), help_text=_('Due At'),
        null=True, blank=True, default=None)

    sent_at = models.DateTimeField(
        _('Sent At'), help_text=_('Sent At'),
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
        '''Add an recipient email address to this Mail

        - email is registered as a :ref:`emailqueue.models.MailAddress`
          for bounce management.
        '''
        to, created = MailAddress.objects.get_or_create(email=email)
        recipient, created = Recipient.objects.get_or_create(
            mail=self, to=to,)
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
        '''Update due_at with `sleep_to` '''
        self.due_at = localtime(now()) + timedelta(days=days)

        # WARN:microsecond is trunctad by MySQL 5.6+
        self.due_at = self.due_at.replace(
            hour=self.sleep_to.hour,
            minute=self.sleep_to.minute,
            second=self.sleep_to.second,
            microsecond=self.sleep_to.microsecond,)
        self.save()

    def delay(self, dt=None):
        '''Mail sending process is delayed until `sleep_to` '''
        dt = dt or localtime(now()).time()

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
                ctx={},         # TODO: deserialize Json
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

    def send_mail(self, recipients=None, due_at=None, *args, **kwargs):
        ''' Send this Mail to all recipients
        :param list(address) recipeints: if None, Recipient list is useed
        :param datetime due_at: if None, self.due_at is used
        '''
        if self.sender and self.sender.server.handler:
            self.sender.server.handler.send_mail(
                self, recipients=None, due_at=None, *args, **kwargs)


class RecipientQuerySet(models.QuerySet):
    def active_set(self, basetime=None):
        basetime = basetime or now()
        return self.filter(
            models.Q(mail__due_at__isnull=True) |
            models.Q(mail__due_at__lte=basetime),
            # mail__enabled=True,
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
        return self.mail.create_message(self.to, encoding=encoding)

    def save(self, *args, **kwargs):
        ''' If return_path is not set, create it before `save` '''
        if not self.return_path and self.mail and self.to:
            self.return_path = utils.to_return_path(
                'mail', self.mail.sender.domain,
                self.mail.id, self.to.id, )

        super(Recipient, self).save(*args, **kwargs)


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
    server = models.ForeignKey(
        Server, verbose_name=_('Recipient Server'),
        default=None, blank=True, null=True)

    sender = models.EmailField(
        _('Sender'), help_text=_('Sender Help'),  max_length=100,
        default=None, blank=True, null=True)

    recipient = models.EmailField(
        _('Recipient'), help_text=_('Recipient Help'), max_length=100,
        default=None, blank=True, null=True)

    forward_sender = models.EmailField(
        _('Forwarding Sender'),
        help_text=_('Fowarding Sender Help'),  max_length=100,
        default=None, blank=True, null=True)

    forward_recipient = models.ForeignKey(
        MailAddress, verbose_name=_('Forwarding Recipient'),
        help_text=_('Forwarding Recipient Help'), max_length=100,
        default=None, blank=True, null=True, on_delete=models.SET_DEFAULT)

    processed_at = models.DateTimeField(
        _('Processed At'), null=True, blank=True, default=None)

    class Meta:
        verbose_name = _(u'Message')
        verbose_name_plural = _(u'Message')

    @property
    def bounced_parameters(self):
        ''' Email Hanlders of Message object
        '''
        def _cached():
            self._bounced_parameters = utils.from_return_path(self.recipient)
            return self._bounced_parameters

        return getattr(self, '_bounced_parameters', _cached())

    @property
    def forward_return_path(self):
        '''Return-Path for forwarding

        - used ofr forwarding error message for Relayed message
        '''
        domain = self.recipient.split('@')[1]
        address = utils.to_return_path(
            "fwd", domain, str(self.id), )
        return address

    def process_message(self):
        ''' Process this Message '''
        if self.server and self.server.handler:
            self.server.handler.process_message(self)


class ReportQuerySet(models.QuerySet):
    def create_from_message(self, message):
        params = message.bounced_parameters
        if not params:
            return None

        try:
            address = MailAddress.objects.get(id=params['to'])

            report, created = self.objects.get_or_create(
                address=address, bounce=message,
                mail=Mail.objects.get(id=params['msg']))

            if created:
                address.bounced = address.bounced + 1
                address.save()
                report.action = message.dsn_action
                report.status = message.dsn_status
                report.save()
            return report
        except:
            pass
        return None


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

    objects = ReportQuerySet.as_manager()
