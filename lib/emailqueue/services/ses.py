from emailqueue.services import Api as ServiceApi
from emailqueue.models import Notification, Service
import boto


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


from tastypie.resources import Resource
#from tastypie.serializers import Serializer
from tastypie.http import HttpCreated
from django.conf.urls import url
from django.core.urlresolvers import reverse
import urlparse
#:import json


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
