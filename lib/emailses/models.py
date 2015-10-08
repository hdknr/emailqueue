from django.db import models
from django.utils.translation import ugettext_lazy as _

from emailqueue.models import BaseModel

import managers
import methods


class Service(BaseModel, methods.Service):
    name = models.CharField(_('Service Name'), max_length=100)

    key = models.CharField(
        _('SES Access Key'),
        max_length=100, null=True, default=None, blank=True)
    secret = models.CharField(
        _('SES Access Secret'),
        max_length=100, null=True, default=None, blank=True)

    settings = models.TextField(
        _('Settings'), null=True, default=None, blank=True)

    class Meta:
        verbose_name = _('SES Service')
        verbose_name_plural = _('SES Service')

    def __unicode__(self):
        return self.name


class Source(BaseModel, methods.Source):
    service = models.ForeignKey(
        Service, null=True, blank=True, default=None, )

    address = models.EmailField(_('Address'), max_length=100)

    arn = models.CharField(
        _('Source Identity Arn'), help_text=_('Source Identity Arn'),
        max_length=100, null=True, default=None, blank=True)

    class Meta:
        verbose_name = _('SES Source')
        verbose_name_plural = _('SES Source')

    def __unicode__(self):
        return self.address


class Topic(BaseModel):
    BOUNCE = 0
    COMPLAINT = 1
    DELIVERY = 2

    service = models.ForeignKey(
        Service, null=True, blank=True, default=None, )

    source = models.ForeignKey(
        Source, null=True, blank=True, default=None, )

    topic = models.IntegerField(
        _('Topic'), choices=(
            (BOUNCE, _('Bounce Topic')),
            (COMPLAINT, _('Complaint Topic')),
            (DELIVERY, _('Delivery Topic')),), default=BOUNCE)

    arn = models.CharField(
        _('Topic Arn'),
        max_length=100, null=True, default=None, blank=True)

    class Meta:
        verbose_name = _('SNS Topic')
        verbose_name_plural = _('SNS Topic')
        unique_together = (('source', 'topic', ), )

    def __unicode__(self):
        return u"{0} {1}".format(
            self.service.__unicode__(),
            self.get_topic_display())


class Notification(BaseModel, methods.Notification):
    topic = models.ForeignKey(
        Topic, null=True, blank=True, default=None, )

    message = models.TextField(
        _('SNS Message'), help_text=_('SNS Message'),)

    headers = models.TextField(
        _('SNS Headers'), help_text=_('SNS Headers Help'),
        null=True, blank=True, default='')

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notification')

    objects = managers.NotificationQuerySet.as_manager()


class Certificate(BaseModel, methods.Certificate):
    service = models.ForeignKey(Service)
    cert_url = models.URLField(_('Certificate URL'))
    cert = models.TextField(
        _('Certificate'), null=True, default=None, blank=True)

    class Meta:
        verbose_name = _('SES Certificate')
        verbose_name_plural = _('SES Certificate')
