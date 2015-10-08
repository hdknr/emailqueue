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


class SnsMessage(object):
    def __init__(self, text):
        self.data = json.loads(text)

    def __getattr__(self, name):
        return self.data.get(name, None)

    def format(self, indent=2, *args, **kwargs):
        return json.dumps(self.data, indent=2, *args, **kwargs)

    @property
    def Message(self):
        def _cache(self):
            self._Message = SesMessage(self.data['Message'])
            return self._Message

        return getattr(self, '_Message', _cache(self))

    def confirm_subscribe_url(self, jobj):
        return requests.get(self.SubscribeURL)

    @property
    def singin_input(self):
        return NOTIFICATION_SIGNING_INPUT(self.data)

    def verify(self, cert):
        return verify_pycrypto(
            cert, self.singin_input, self.Signature)


class SesMessage(object):
    def __init__(self, text):
        self.data = json.loads(text)


class Api(object):

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
