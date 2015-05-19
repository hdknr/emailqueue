from django.test import TestCase
from urllib import urlencode

from models import Mail, Postbox, Recipient
from django.utils.timezone import now
from datetime import timedelta


class MailTest(TestCase):
    def post_json(
            self, url, jstr="{}", status_code=200, user=None,
            meta={}, query={}):
        meta['content_type'] = 'application/json'

        if query:
            url = url + "?" + urlencode(query)

        response = self.client.post(url, data=jstr, **meta)
        self.assertEqual(response.status_code, status_code)
        return response

    def _create_mail(self):
        pb = Postbox.objects.get_or_create(
            address='admin@test.oillio.net',
            forward='oillionet@ict-tact.co.jp',
        )[0]
        mail = Mail.objects.create(
            sender=pb,
            subject='subject',
            body='body',
        )
        return mail

    def test_active_mail(self):
        mail = self._create_mail()

        # Default
        dtnow = now()
        self.assertIsNone(mail.due_at)
        self.assertFalse(mail.enabled)
        self.assertTrue(Mail.objects.filter(due_at__isnull=True).exists())
        self.assertTrue(Mail.objects.filter(due_at__isnull=True).exists())
        self.assertFalse(Mail.objects.filter(due_at__lte=dtnow).exists())
        self.assertFalse(Mail.objects.active_set().exists())

        # Set Enabled
        mail.enabled = True
        mail.save()
        self.assertTrue(Mail.objects.filter(due_at__isnull=True).exists())
        self.assertFalse(Mail.objects.filter(due_at__lte=dtnow).exists())
        self.assertTrue(Mail.objects.active_set().exists())

        # Set Time
        dtold = dtnow + timedelta(days=-1)
        mail.due_at = dtold
        mail.save()
        self.assertFalse(Mail.objects.filter(due_at__isnull=True).exists())
        self.assertTrue(Mail.objects.filter(due_at__lte=dtnow).exists())
        self.assertTrue(Mail.objects.active_set().exists())

        # Set Future Time ( Mail IS NOT SENT now! )
        dtnew = dtnow + timedelta(days=+1)
        mail.due_at = dtnew
        mail.save()
        self.assertFalse(Mail.objects.filter(due_at__isnull=True).exists())
        self.assertFalse(Mail.objects.filter(due_at__lte=dtnow).exists())
        self.assertFalse(Mail.objects.active_set().exists())

    def test_active_recipient(self):
        mail = self._create_mail()
        mail.enabled = True
        mail.save()

        recipient = mail.add_recipient('you@domain.com')
        self.assertIsNone(recipient.sent_at)
        self.assertIsNone(mail.due_at)

        # enabled Mail
        self.assertTrue(Recipient.objects.active_set().exists())

        # Set Time
        mail.due_at = now() + timedelta(days=-1)
        mail.save()
        self.assertTrue(Recipient.objects.active_set().exists())

        # Set Time(Future) Not Sent
        mail.due_at = now() + timedelta(days=1)
        mail.save()
        self.assertFalse(Recipient.objects.active_set().exists())

        #  Recipient alread sent
        mail.due_at = None
        mail.save()
        recipient.sent_at = now()
        recipient.save()
        self.assertTrue(Mail.objects.active_set().exists())
        self.assertFalse(Recipient.objects.active_set().exists())

        # Add New Recipient
        mail.add_recipient('other@domain.com')
        self.assertTrue(Mail.objects.active_set().exists())
        self.assertEqual(Recipient.objects.active_set().count(), 1)
        self.assertEqual(Recipient.objects.count(), 2)

    def test_delay(self):
        mail = self._create_mail()
        mail.enabled = True
        mail.save()

        self.assertIsNone(mail.due_at)
        dt_now = now()
        dt_sleep_from = dt_now - timedelta(minutes=1)
        dt_sleep_to = dt_now + timedelta(minutes=1)

        # ms is truncated by MySQL 5.6+
        dt_sleep_from = dt_sleep_from.replace(microsecond=0)
        dt_sleep_to = dt_sleep_to.replace(microsecond=0)

        mail.sleep_from = dt_sleep_from.time()
        mail.sleep_to = dt_sleep_to.time()

        self.assertTrue(mail.is_active())
        self.assertIsNone(mail.due_at)
        self.assertTrue(mail.delay())           # This Mail MUST NOT be sent

        mail2 = Mail.objects.get(id=mail.id)     # reoad

        self.assertIsNotNone(mail2.due_at)
        self.assertEqual(mail2.due_at, dt_sleep_to)
        self.assertFalse(mail2.is_active())
