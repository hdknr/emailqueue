from django.db import models
from django.utils.translation import ugettext_lazy as _
from enum import Enum

ServiceType = dict(
    ses=(0, _(u'Amazon SES')), 
    smtp=(1, _(u'SMTP Server'))))
)
    



class EnumField(models.IntegerField):
    def __init__(self, verbose_name=None,  enum={}, **kwargs):
        kwargs['choices'] = tuple(v for k, v in enum.items())
        super(EnumField, self).__init__(verbose_name=verbose_name, **kwargs) 

    @property
    def enum(self):
#        return type('FieldEnum',(Enum,) ,dict((k, v[0]), self.enum))
        return None


class Service(models.Model):
    service = EnumField(_(u'Service Type'),
        enum = dict(ses=(0, _(u'Amazon SES')), smtp=(1, _(u'SMTP Server'))))


class Email(models.Model):
    address_from = models.CharField(_(u'From Address'), max_length=50)
    address_to = models.CharField(_(u'From Address'), max_length=50)
    address_return_path = models.CharField(
        _(u'Return Path Address'), max_length=50)

    message = models.TextField(_(u'Raw Message'))
    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )
