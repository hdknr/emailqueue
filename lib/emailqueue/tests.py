from django.test import TestCase
from django.core.urlresolvers import reverse
from urllib import urlencode


class NotificationTest(TestCase):
    def post_json(
            self, url, jstr="{}", status_code=200, user=None,
            meta={}, query={}):
        meta['content_type'] = 'application/json'

        if query:
            url = url + "?" + urlencode(query)

        response = self.client.post(url, data=jstr, **meta)
        self.assertEqual(response.status_code, status_code)
        return response

    def test_simple(self):
        from emailqueue.models import Service, ServiceType, Notification
        service = Service(service_type=ServiceType.ses.value)
        service.save()
        url = service.service.notify_path()
        self.post_json(url, status_code=201)
        self.assertEqual(Notification.objects.count(), 1)
