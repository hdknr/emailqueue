# -*- coding: utf-8 -*-

from pycommand.djcommand import Command as PyCommand, SubCommand
# from django.utils.translation import ugettext as _
from emailqueue.models import (
    Service,
)
# import sys


class Command(PyCommand):
    managers = ['manage.py', ]

    class ServiceList(SubCommand):
        name = "list_service"
        description = "List Servcices"
        args = [
        ]

        def run(self, params, **options):
            for service in Service.objects.all():
                print service.id, ":", service.service.name, service.key

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

    class ActiveMailList(SubCommand):
        name = "list_active_mail"

        def run(self, params, **options):
            from emailqueue.models import Mail
            for mail in Mail.objects.active_set():
                print mail.id
