from django.test import TestCase
from django.conf import settings
from emailqueue import models


class QueueTest(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.server = models.Server.objects.create(
            name='myservice',
            domain='service.deb',)

        forward = models.MailAddress.objects.create(
            email='me@origin.deb',)

        self.me = models.Postbox.objects.create(
            server=self.server,
            address='me@' + self.server.domain,
            forward=forward)

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

    def test_bounced_mail(self):
        ''' Bounce handling to Mail
        '''
        models.MailAddress.objects.all().delete()
        models.Recipient.objects.all().delete()
        models.Message.objects.all().delete()
        mail = models.Mail.objects.create(
            sender=self.me,
            subject='test',
            body='text')

        recipient = mail.add_recipient('you@target.com')

        self.assertEquals(models.Recipient.objects.count(), 1)
        self.assertEquals(models.MailAddress.objects.count(), 1)

        bounced_message = models.Message.objects.create(
            server=mail.sender.server,
            sender='mailer-daemon@' + recipient.to.domain,
            recipient=recipient.return_path,
            raw_message=recipient.create_message())

        self.assertEquals(models.Message.objects.count(), 1)
        to = models.MailAddress.objects.get(id=recipient.to.id)
        self.assertEquals(to.bounced, 0)

        bounced_message.process_message()

        to = models.MailAddress.objects.get(id=recipient.to.id)
        self.assertEquals(to.bounced, 1)
