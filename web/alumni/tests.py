from django.test import TestCase


class AlumniTest(TestCase):
    '''
        ./manage.py dumpdata --natural
            --exclude auth.permission --exclude contenttypes
                --indent 4 > alumni/fixtures/test.json
    '''
    fixtures = ['test.json']

    def setUp(self):
        from alumni import models
        self.assertEqual(2, models.Alumnus.objects.count())

        from emailqueue.models import Contact
        self.assertEqual(4, Contact.objects.count())

    def test_send(self):
        from emailqueue.models import Outbound
        # print [n for n in dir(self) if n.startswith('assert')]
        self.assertTrue(0 < Outbound.objects.count())
        Outbound.objects.all()[0].send()


