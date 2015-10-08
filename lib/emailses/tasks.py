from __future__ import absolute_import
from django.dispatch import receiver
from emailses import models

import logging
logger = logging.getLogger('emailses')


@receiver(models.Notification.confirm_signal, sender=models.Notification)
def confirm(instance, *args, **kwargs):
    # access url # TODO: error logging
    instance.message_object.confirm_subscribe_url()


@receiver(models.Notification.bounce_signal, sender=models.Notification)
def bounce(instance, *args, **kwargs):
    print instance.message_object.Message.bounce.format()


@receiver(models.Notification.delivery_signal, sender=models.Notification)
def delivery(instance, *args, **kwargs):
    # TODO: most of cases, delete notification
    logger.debug(instance.message_object.Message.delivery.format())


@receiver(models.Notification.complaint_signal, sender=models.Notification)
def complaint(instance, *args, **kwargs):
    print instance.message_object.Message.complaint.format()
