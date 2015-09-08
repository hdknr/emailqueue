from django.apps import AppConfig as DjangoAppConfig
from django.utils.translation import (
    ugettext_lazy as _,
)


class AppConfig(DjangoAppConfig):
    name = 'emailqueue'
    verbose_name = _("Emailqueue")

    def ready(self):
        import tasks        # NOQA
