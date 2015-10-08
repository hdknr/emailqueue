from django.apps import AppConfig as DjangoAppConfig
from django.utils.translation import (
    ugettext_lazy as _,
)


class AppConfig(DjangoAppConfig):
    name = 'emailses'
    verbose_name = _("Emailses")

    def ready(self):
        import tasks        # NOQA
