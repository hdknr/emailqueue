from django.db import models
from django.utils.translation import ugettext_lazy as _

from emailqueue.models import BaseModel

import managers


class Notification(BaseModel):
    message = models.TextField(
        _('SNS Message'), help_text=_('SNS Message'),)

    headers = models.TextField(
        _('SNS Headers'), help_text=_('SNS Headers Help'),
        null=True, blank=True, default='')

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notification')

    objects = managers.NotificationQuerySet.as_manager()
