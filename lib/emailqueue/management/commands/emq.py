# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from pycommand.command import Command as PyCommand, SubCommand
#from django.utils.translation import ugettext as _
from emailqueue.models import Service, ServiceType, Email
import sys


class Command(BaseCommand, PyCommand):
    managers = ['manage.py', ]

    def run_from_argv(self, argv):
        return self.run(argv)

    class ServiceList(SubCommand):
        name = "list_service"
        description = "List Servcices"
        args = [
        ]

        def run(self, params, **options):
            for service in Service.objects.all():
                print service.id, ":", service.service.name, service.key


    class EmailCreate(SubCommand):
        name = "create_email"
        description = "Describe an Email"
        args = [
            (('id',), dict(nargs=1, type=int, help="Service ID")),
            (('addr_from',), dict(nargs=1,  help="From Address")),
            (('addr_to',), dict(nargs=1,  help="To Address")),
            (('subject',), dict(nargs=1,  help="Subject")),
            (('message',), dict(nargs='?', default="",  help="Message")),
            (('--schedule', '-S'), dict(default=None,  help="Schedule to Send Message")),
            (('--file', '-F'), dict(default=None, help="Message File")),
            
        ]

        def run(self, params, **options):
            if params.file  == "stdin":
                if sys.stdin.isatty():
                    print _(u"stdin is not specified.")
                    return 
                params.message = sys.stdin.read()
            elif params.file:
                params.message = open(paramrs.file).read()

            #: TODO: schedule is parsed datatime
 
            email = Email.create_email(
                service=params.id[0],
                addr_from=params.addr_from[0], 
                addr_to=params.addr_to[0], 
                subject=params.subject[0],
                message=params.message,
                schedule=params.schedule)

            print email.id, email.message_id_hash


    class EmailList(SubCommand):
        name = "list_email"
        description = "List Emails"
        args = [
            (('id',), dict(nargs=1, type=int, help="Service ID")),
        ]

        def run(self, params, **options):
            for email in Email.objects.filter(service__id=params.id[0]):
                print email.id, ":", email.message_id_hash 


    class EmailDescription(SubCommand):
        name = "desc_email"
        description = "Describe an Email"
        args = [
            (('id',), dict(nargs=1, type=int, help="Emailid")),
        ]

        def run(self, params, **options):
            email = Email.objects.get(id=params.id[0])
            print "ID:", email.id
            print "Message ID Hash:", email.message_id_hash
            print "Return Path:", email.address_return_path
            print "Raw Message:\n\n", email.message


    class EmailDelete(SubCommand):
        name = "delete_email"
        description = "Delete an Email"
        args = [
            (('id',), dict(nargs='+', type=int, help="Email ID")),
        ]

        def run(self, params, **options):
            Email.objects.filter(id__in=params.id).delete()


    class EmailSend(SubCommand):
        name = "send_email"
        description = "Send an Email"
        args = [
            (('id',), dict(nargs='+', type=int, help="Email ID")),
        ]

        def run(self, params, **options):
            for email in Email.objects.filter(id__in=params.id):
                email.send()


    class AddressVerify(SubCommand):
        name = "verify_address"
        description = "Verify an Email Address"
        args = [
            (('id',), dict(nargs=1, type=int, help="Service ID")),
            (('address',), dict(nargs='+', help="Email Address")),
        ]

        def run(self, params, **options):
            service = Service.objects.get(id=params.id[0])
            for addr in params.address:
                service.service.verify(addr)
