from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.importlib import import_module

from email.mime.text import MIMEText
from email import Charset

from emailqueue.utils import Enum
import uuid
from hashlib import sha256

ServiceType = Enum(
    'ServiceType',
    ses=(0, _(u'Amazon SES')),
    smtp=(1, _(u'SMTP Server')),
)

CREDENTIAL = lambda length: dict(
    max_length=length, null=True, blank=True, default=None, )

TIME = lambda: dict(
    null=True, blank=True, default=None, )

NULLABLE = TIME


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
    notify_uri = models.CharField(_("Notify URI"),  **CREDENTIAL(200))

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

    def send(self, email):
        return self.service.send(email)


class Notification(BaseModel):
    service = models.ForeignKey(Service, **NULLABLE())
    message = models.TextField(_(u'Notification Message'))


class Email(BaseModel):
    service = models.ForeignKey(Service)
    address_from = models.CharField(_(u'From Address'), max_length=50)
    address_to = models.CharField(_(u'To Address'), max_length=50)
    address_return_path = models.CharField(
        _(u'Return Path Address'), max_length=50)
    message_id_hash = models.CharField(_(u'Message ID Hash'), max_length=100)
    message = models.TextField(_(u'Raw Message'))

    schedule = models.DateTimeField(_(u'Schedule'), **TIME())
    sent_at = models.DateTimeField(_(u'Sent At'),  **TIME())

    def send(self):
        self.service.send(self)

    @classmethod
    def create_email(
        cls, service, addr_from, addr_to,
        subject, message,
        message_id=None, return_address=None,
        subtype="plain", encoding="utf-8",
        schedule=None
    ):

        if isinstance(service, int):
            service = Service.objects.get(id=service)

        message_id = message_id or uuid.uuid1().hex
        message_id_hash = sha256(message_id).hexdigest()

        if encoding == 'utf-8':
            pass
        elif encoding == "shift_jis":
            #: DoCoMo
            #: TODO chekck message encoding and convert it
            Charset.add_charset(
                'shift_jis', Charset.QP, Charset.BASE64, 'shift_jis')
            Charset.add_codec('shift_jis', 'cp932')

        message = MIMEText(message, subtype, encoding)
        message['Subject'] = subject
        message['From'] = addr_from
        message['To'] = addr_to
        message['Message-ID'] = message_id

        user, domain = addr_from.split('@')
        if return_address:
            return_address = return_address.replace8('@', '=')
        else:
            return_address = message_id_hash

        return_path = "%s+%s@%s" % (
            user, return_address, domain,
        )

        email = cls(
            service=service,
            address_from=addr_from,
            address_to=addr_to,
            address_return_path=return_path,
            message_id_hash=message_id_hash,
            message=message.as_string(),
            schedule=schedule,
        )
        email.save()
        return email
