# from django.db import models
from django.utils.translation import ugettext_lazy as _

from emailqueue.models import Service
import tasks


class SmtpServer(Service):
    class Meta:
        verbose_name = _('SMTP Server')
        verbose_name_plural = _('SMTP Server')

    def save(self, *args, **kwargs):
        self.class_name = 'smtpserver'
        super(SmtpServer, self).save(*args, **kwargs)

    def send(self, outbound):
        tasks.send_raw_message(
            outbound.return_path,
            [outbound.recipient.email],
            outbound.raw_message,
        )
