from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.importlib import import_module


from emailqueue.utils import Enum

ServiceType = Enum(
    'ServiceType',
    ses=(0, _(u'Amazon SES')),
    smtp=(1, _(u'SMTP Server')),
)

CREDENTIAL = lambda length: dict(
    max_length=length, null=True, blank=True, default=None, )


class BaseModel(models.Model):
    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )

    class Meta:
        abstract = True


class Service(BaseModel):
    service_type = models.IntegerField(
        _(u'Service Type'), choices=ServiceType.choices,)
    user = models.CharField(_("Service User"), **CREDENTIAL(50))
    key = models.CharField(_("Service Key"),  **CREDENTIAL(100))
    secret = models.CharField(_("Service Secret"),  **CREDENTIAL(100))
    region = models.CharField(_("Service Region"),  **CREDENTIAL(50))

    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        self._service = None

    @property
    def service(self):
        if self._service is None and self.service_type is not None:
            name = ServiceType(self.service_type).name
            mod = import_module('emailqueue.services.%s' % name)
            self._service = getattr(mod, 'Api')(self)
        return self._service


class Email(BaseModel):
    address_from = models.CharField(_(u'From Address'), max_length=50)
    address_to = models.CharField(_(u'From Address'), max_length=50)
    address_return_path = models.CharField(
        _(u'Return Path Address'), max_length=50)

    message = models.TextField(_(u'Raw Message'))
