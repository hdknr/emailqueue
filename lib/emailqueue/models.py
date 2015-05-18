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
# import hashlib
from email.mime.text import MIMEText
from email import Charset


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


class Service(BaseModel):
    ''' Mail Sending Service
    '''
    name = models.CharField(
        _('Mail Service Name'), unique=True, max_length=50)
    class_name = models.CharField(
        _('Mail Service Class Name'), max_length=20)

    class Meta:
        verbose_name = _('Mail Service')
        verbose_name_plural = _('Mail Service')

    def __unicode__(self):
        return self.name

    @property
    def instance(self):
        return getattr(self, self.class_name)

    def send(self, email):
        raise NotImplemented


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

    class Meta:
        verbose_name = _('Mail Address')
        verbose_name_plural = _('Mail Address')

    def __unicode__(self):
        return self.email


class MailQuerySet(models.QuerySet):
    def active_set(self, basetime=None):
        basetime = basetime or now()
        return self.filter(
            models.Q(due_at__isnull=True) | models.Q(due_at__lte=basetime),
            enabled=True,
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

    class Meta:
        verbose_name = _('Mail')
        verbose_name_plural = _('Mail')

    objects = MailQuerySet.as_manager()

    def __unicode__(self):
        return self.subject

    def add_recipient(self, email):
        to = MailAddress.objects.get_or_create(email=email)[0]
        recipient = Recipient.objects.get_or_create(
            mail=self, to=to,
            return_path='emq-{0}-{1}@{2}'.format(
                self.id, to.id, self.sender.domain,
            ),)[0]
        return recipient

    @property
    def subtype(self):
        # TODO: SHOULD BE configurable
        return 'plain'


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

    def rendered_message(self):
        return template.Template(self.mail.body).render(
            template.Context(dict(
                to=self.to,
                ctx=self.mail.ctx,
            )))

    def create_message(self, encoding="utf-8",):
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
            self.rendered_message(), self.mail.subtype, encoding)

        message['Subject'] = self.mail.subject
        message['From'] = self.mail.sender.address
        message['To'] = self.to.email
        message['Message-ID'] = message_id

        return message


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
