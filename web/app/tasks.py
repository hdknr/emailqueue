from django.dispatch import receiver
from emailqueue import models

MAX_BOUNCED = 3


@receiver(models.MailAddress.bounced_signal, sender=models.MailAddress)
def on_mail_bounced(instance, **kwargs):
    if instance.bounced > MAX_BOUNCED:
        instance.enabled = False
        instance.save()
