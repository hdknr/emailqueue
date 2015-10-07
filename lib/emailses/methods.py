import json
from datetime import datetime
from enum import Enum

import ses


class BaseObjectSerializer(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, object):
            return ''

        return super(BaseObjectSerializer, self).default(obj)

    @classmethod
    def dumps(cls, obj, *args, **kwargs):
        kwargs['cls'] = cls
        return json.dumps(obj, *args, **kwargs)


class Service(object):

    def cert(self, url):
        cert = self.certificate_set.filter(cert_url=url).first()
        if not cert:
            cert = self.certificate_set.create(
                cert_url=url,
                cert=ses.get_cert(url))
        return cert


class Notification(object):

    @property
    def _topic(self):
        if not self.topic_id:
            field, d, d, d = self._meta.get_field_by_name('topic')
            self.topic = field.related_model.objects.filter(
                arn=ses.TOPIC(self.message_object)).first()
            if self.topic:
                self.save()
        return self.topic_id and self.topic

    @property
    def cert(self):
        topic = self._topic
        return topic.service.cert(ses.CERT_URL(self.message_object))

    @property
    def message_object(self):
        def _cache():
            self._message_object = json.loads(self.message)
            return self._message_object

        return getattr(self, '_message_object', _cache())

    @property
    def headers_object(self):
        def _cache():
            self._headers_object = json.loads(self.headers)
            return self._headers_object

        return getattr(self, '_headers_object', _cache())

    @property
    def signing_input(self):
        return ses.NOTIFICATION_SIGNING_INPUT(self.message_object)

    @property
    def signature(self):
        return ses.SIGNATURE(self.message_object)

    def is_valid(self):
        cert = self.cert
        return cert and cert.verify(self.signing_input, self.signature) or False


class Certificate(object):

    def verify(self, signing_input, signature):
        return ses.verify_pycrypto(self.cert, signing_input, signature)
