from django.db import models
from django.utils.translation import ugettext_lazy as _


class Email(models.Model):
    address_from = models.CharField(_(u'From Address'), max_length=50)
    address_to = models.CharField(_(u'From Address'), max_length=50)
    address_return_path = models.CharField(
        _(u'Return Path Address'), max_length=50)

    message = models.TextField(_(u'Raw Message'))
    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )
