from django.test import TestCase
from django.conf import settings
from emailqueue import models


class QueueTest(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.server = models.Server.objects.create(
            name='myservice',
            domain='service.deb',)

        self.me = models.Postbox.objects.create(
            server=self.server,
            address='me@' + self.server.domain,
            forward='me@origin.deb',)

    def test_return_path(self):
        ''' test return path address
        '''
        from emailqueue import utils

        # not return_path, "direct" message
        a = utils.from_return_path('test@domain.com')
        self.assertEquals(a['handler'], 'direct')
        self.assertEquals(a['domain'], 'domain.com')
        self.assertEquals(len(a['args']), 0)

        # construct return path for 'fwd'
        handler = 'fwd'
        args = ('9', '11')
        domain = 'domain.com'
        return_path = utils.to_return_path(handler, domain, *args)
        # print "return_path:", return_path

        # parese return_path
        a = utils.from_return_path(return_path)
        self.assertEquals(a['handler'], handler)
        self.assertEquals(a['domain'], domain)
        self.assertEquals(a['args'], args)
