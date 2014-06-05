from __future__ import absolute_import

from celery import shared_task
from .models import BounceAddress


@shared_task
def countup(id, counts=1):
    address = BounceAddress.objects.get(id=id)
    address.count = address.count + counts
    address.save()
