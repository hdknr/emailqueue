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


def NOTIFICATION_SIGNING_INPUT(jobj):
    return "".join([
        "%s\n%s\n" % (k, jobj.get(k))
        for k in NOTIFICATION_SIGNING_INPUT_KEY
        if k in jobj
    ])


def SIGNATURE(jobj):
    return jobj['Signature']


def CERT_URL(jobj):
    return jobj['SigningCertURL']


def TOPIC(jobj):
    return jobj.get('TopicArn', '')


def get_cert(url):
    res = requests.get(url)
    return res.text


from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Util.asn1 import DerSequence
from Crypto.Signature import PKCS1_v1_5

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


class Api(object):
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
        # return SnsResource().get_resource_uri() + "%d/" % self.service.id
        return ''

    def verify_notification(self, notification):
        jobj = notification.json_message

        if not jobj:
            return False

        sinput = NOTIFICATION_SIGNING_INPUT(jobj)

        if not self.service.public_key:
            res = requests.get(jobj['SigningCertURL'])
            self.service.public_key = res.text
            self.service.save()

        return verify_pycrypto(
            self.service.public_key, sinput, jobj['Signature'])

    def process_notification(self, notification):
        if not self.verify_notification(notification):
            return
        #: TODO: check other information...

        jobj = notification.json_message
        message = jobj and json.loads(jobj.get('Message', '{}'))
        if message and message.get('notificationType') == 'Bounce':
            bounces = message.get('bounce', {}).get('bouncedRecipients', [])
            for bounce in bounces:
                addr = bounce.get('emailAddress', None)
                if not addr:
                    continue

                address, created = \
                    self.service.bounceaddress_set.get_or_create(
                        address=addr
                    )
                # BounceLog(address=address, message=json.dumps(bounce)).save()
                # TODO: recalcualte BounceAddress count
