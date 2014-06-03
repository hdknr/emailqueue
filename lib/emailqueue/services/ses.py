from emailqueue.services import Api as ServiceApi
from emailqueue.models import Notification, Service
import boto
import json
import requests

# http://docs.aws.amazon.com/sns/latest/dg/
# SendMessageToHttp.verify.signature.html

NOTIFICATION_SIGNING_INPUT_KEY = [
    "Message",
    "MessageId",
    "Subject",
    "SubscribeURL",
    "Timestamp",
    "Token",
    "TopicArn",
    "Type",
]

NOTIFICATION_SIGNING_INPUT = lambda jobj:\
    "".join([
        "%s\n%s\n" % (k, jobj.get(k))
        for k in NOTIFICATION_SIGNING_INPUT_KEY
        if k in jobj
    ])


from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Util.asn1 import DerSequence
from Crypto.Signature import PKCS1_v1_5
#from Crypto.Util import number

from base64 import b64decode, standard_b64decode


def import_pubkey_from_x509(pem):
    b64der = ''.join(pem.split('\n')[1:][:-2])
    cert = DerSequence()
    cert.decode(b64decode(b64der))

    tbs_certificate = DerSequence()
    tbs_certificate.decode(cert[0])

    subject_public_key_info = tbs_certificate[6]

    return RSA.importKey(subject_public_key_info)


def verify_pycrypto(pem, signing_input, b64signature):
    pub = import_pubkey_from_x509(pem)
    verifier = PKCS1_v1_5.new(pub)

    sig = standard_b64decode(b64signature)
    signing_input = signing_input.encode('utf8')
    dig = SHA.new(signing_input)

    return verifier.verify(dig, sig)


class Api(ServiceApi):
    name = "Amazon SES"

    def __init__(self, service):
        self.service = service
        self._conn = None

    @property
    def connection(self):
        if self._conn is None:
            self._conn = boto.connect_ses(
                aws_access_key_id=self.service.key,
                aws_secret_access_key=self.service.secret)

        return self._conn

    def send(self, email):
        self.connection.send_raw_email(
            raw_message=email.message,
            source=email.address_from,
            destinations=email.address_to
        )

    def verify(self, address):
        self.connection.verify_email_address(address)

    def notify_path(self):
        return SnsResource().get_resource_uri() + "%d/" % self.service.id

    def verify_notification(self, notification):
        jobj = json.loads(notification.message)
        sinput = NOTIFICATION_SIGNING_INPUT(jobj)

        if not self.service.public_key:
            res = requests.get(jobj['SigningCertURL'])
            self.service.public_key = res.text
            self.service.save()

        return verify_pycrypto(
            self.service.public_key, sinput, jobj['Signature'])


from tastypie.resources import Resource
#from tastypie.serializers import Serializer
from tastypie.http import HttpCreated
from django.conf.urls import url
from django.core.urlresolvers import reverse
import urlparse


class SingletonResource(Resource):

    @classmethod
    def url_name(cls):
        return "%s_detail" % cls.Meta.resource_name

    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        return [
            url(
                r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, ''),
                self.wrap_view('dispatch_detail'),
                name=self.url_name())
        ]

    @classmethod
    def url(cls, host='', *args, **kwargs):
        kwargs['resource_name'] = cls.Meta.resource_name
        kwargs = dict(
            tuple([(k, v) for k, v in kwargs.items() if v is not None]))
        ret = urlparse.urljoin(host, reverse(cls.url_name(), kwargs=kwargs))
        return ret


class SnsResource(Resource):

    class Meta:
        allowed_methods = ['post', ]
        resource_name = 'sns'

    def post_detail(self, request, pk=None, resource_name=None, **kwargs):
        Notification(
            service=Service.objects.get(id=pk),
            message=request.body).save()
        return HttpCreated()
