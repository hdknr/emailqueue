import json
from datetime import datetime
from enum import Enum

import boto
import requests

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
                cert=requests.get(url).text)
        return cert

    @property
    def connection(self):
        def _cache():
            self._conn = boto.connect_ses(
                aws_access_key_id=self.key,
                aws_secret_access_key=self.secret)
            return self._conn

        return getattr(self, '_conn', _cache())


class Source(object):
    @property
    def connectiont(self):
        return self.service.connection

    def cert(self, url):
        return self.service.cert(url)

    def send_raw_message(self, addr_from, addr_to, raw_message):
        self.connection.send_raw_email(
            raw_message=raw_message,
            source=addr_from,
            destinations=addr_to,
        )

    def verify_address(self, address):
        '''
        http://boto.readthedocs.org/en/latest/ses_tut.html
        #verifying-a-sender-email-address
        '''
        self.connection.verify_email_address(address)


class Notification(object):

    @property
    def message_object(self):
        def _cache():
            self._message_object = ses.SnsMessage(self.message)
            return self._message_object

        return getattr(self, '_message_object', _cache())

    @property
    def headers_object(self):
        def _cache():
            self._headers_object = json.loads(self.headers)
            return self._headers_object

        return getattr(self, '_headers_object', _cache())

    @property
    def _topic(self):
        if not self.topic_id:
            field, d, d, d = self._meta.get_field_by_name('topic')
            self.topic = field.related_model.objects.filter(
                arn=self.message_object.TopicArn).first()
            if self.topic:
                self.save()
        return self.topic_id and self.topic

    @property
    def cert(self):
        topic = self._topic
        return topic.source.cert(self.message_object.SigningCertURL)

    def is_valid(self):
        cert = self.cert
        return self.message_object.verify(cert.cert)

    def process(self):
        dict(
            SubscriptionConfirmation=self.do_confirm,
            UnsubscribeConfirmation=self.do_confirm,
            Notification=self.do_notify,
            Default=lambda: None,
        ).get(ses.TYPE(self.message_object.Type), 'Default')()

    def do_confirm(self):
        self.message_object.confirm_subscribe_url()

    def do_notify(self):
        msg = self.message_object.Message       # SesMessage
        dict(
            Bounce=self.do_payload_bounce,
            Complaint=self.do_payload_complaint,
            Default=self.do_payload_nothing,
        ).get(msg.notificationType, 'Default')()
        pass

    def do_payload_bounce(self):
        pass

    def do_payload_complaint(self):
        pass

    def do_payload_nothing(self):
        pass


class Certificate(object):
    pass
