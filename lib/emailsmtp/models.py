from django.db import models
from django.utils.translation import ugettext_lazy as _

import time

from emailqueue.models import BaseModel


class Server(BaseModel):
    name = models.CharField(
        _('Mail Service Name'), unique=True, max_length=50)

    domain = models.CharField(
        _('Mail Domain Name'), unique=True, max_length=50)

    backend = models.CharField(
        _('Mail Backend'), max_length=100,
        default='django.core.mail.backends.smtp.EmailBackend',)

    wait_every = models.IntegerField(
        _('Wait sending for every count'),
        help_text=_('Wait sending for every count help'),
        default=0)

    wait_ms = models.IntegerField(
        _('Wait milliseconds'),
        help_text=_('Wait milliseconds help'),
        default=0)

    class Meta:
        verbose_name = _('SMTP Server')
        verbose_name_plural = _('SMTP Server')

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self._every = 0

    def wait(self):
        self._every = self._every + 1
        if self.wait_every < self._every:
            self._every = 0
            if self.wait_every > 0:
                time.sleep(self.wait_ms / 1000.0)
