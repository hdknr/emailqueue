from django.test import TestCase
from django.conf import settings
from emailqueue import models


class MailTest(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.server = models.Server.objects.create(
            name='myservice',
            domain='service.deb',)

        self.me = models.Postbox.objects.create(
            server=self.server,
            address='me@' + self.server.domain,
            forward='me@origin.deb',)

    def test_simple(self):
        models.Message.objects.all().delete()
        recipient = 'you@target.deb'
        mail = models.Mail.objects.create(
            sender=self.me,
            name='test',
            subject='test-subject',
            body='test-body')

        self.me.server.handler.send_mail(mail, [recipient])
        self.assertEqual(1, models.Message.objects.count())

    def test_forward(self):
        models.Message.objects.all().delete()
        models.Relay.objects.all().delete()
        models.MailAddress.objects.all().delete()

        server_src = models.Server.objects.create(
            name='src',
            domain='src.deb',)

        server_dst = models.Server.objects.create(
            name='dst',
            domain='dst.deb',)

        sender = self.server.postbox_set.create(
            address='man@' + server_src.domain,
            forward='man@' + server_src.domain)

        recipient = self.server.postbox_set.create(
            address='man@' + self.server.domain,
            forward='man@' + server_dst.domain)

        mail = models.Mail.objects.create(
            sender=sender,
            name='test-forward',
            subject='test-forward-subject',
            body='test-foward-body')

        # STEP1. sender -> recipient
        #
        self.me.server.handler.send_mail(
            mail, [recipient.address])
        # MailAddress is created for new outbound mail
        self.assertEqual(1, models.MailAddress.objects.count())
        self.assertEqual(models.MailAddress.objects.first().email,
                         recipient.address)

        # Save to Message because no SMTP connection(in TEST)
        self.assertEqual(1, models.Message.objects.count())
        message = models.Message.objects.first()
        self.assertEquals(message.server, recipient.server)

        # STEP2. recipient -> forwarded recipient
        # because recipient.address is registerd at Postbox
        message.process_message()

        self.assertEqual(2, models.Message.objects.count())
        forwarded_message = models.Message.objects.filter(
            recipient=recipient.forward).first()
        self.assertIsNotNone(forwarded_message)
        self.assertNotEquals(forwarded_message, message)

        self.assertEquals(forwarded_message.recipient, recipient.forward)
        mo = forwarded_message.mailobject
        self.assertEquals(mo['To'], recipient.address)
        self.assertEquals(mo['From'], sender.address)

        self.assertEqual(forwarded_message.sender, message.forward_sender)
        self.assertEqual(forwarded_message.recipient, message.forward_recipient)

        # Relay map MUST be creaed
        self.assertEqual(1, models.Relay.objects.count())
        relay = models.Relay.objects.first()
        self.assertEqual(relay.sender.email,  message.sender)
        self.assertEqual(relay.postbox,  recipient)

        # MailAddress is created for new Relay sender
        self.assertEqual(2, models.MailAddress.objects.count())
        self.assertTrue(
            models.MailAddress.objects.filter(id=relay.sender.id).exists())
