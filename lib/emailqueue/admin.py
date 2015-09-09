from django.contrib import admin
from django.apps import apps
from django.utils.translation import ugettext_lazy as _
from django import forms


import models


class MailAddressAdmin(admin.ModelAdmin):
    search_fields = ['email', ]


class RecipientAdmin(admin.ModelAdmin):
    raw_id_fields = ['mail', 'to', ]
    list_excludes = ('created_at', )
    date_hierarchy = 'sent_at'


class PostboxAdmin(admin.ModelAdmin):
    raw_id_fields = ['forward', ]


class RelayAdmin(admin.ModelAdmin):
    raw_id_fields = ['sender', 'postbox', ]


class ReportAdmin(admin.ModelAdmin):
    raw_id_fields = ['address', 'mail', 'bounce', ]


class MessageAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    actions = ['process_message', ]
    list_filter = ['service', 'server', ]

    def process_message(self, request, queryset):
        for instance in queryset:
            if instance.server and instance.server.handler:
                instance.server.handler.process_message(instance)

    process_message.short_description = _('Process Message')


class MailAdminForm(forms.ModelForm):
    force_send = forms.BooleanField(
        label=_('Force Send This Mail'), initial=False, required=False)

    class Meta:
        model = models.Mail
        exclude = []

    def save(self, *args, **kwargs):
        if self.cleaned_data.get('force_send', False):
            self.instance.reset_status()

        instance = super(MailAdminForm, self).save(*args, **kwargs)

        if self.cleaned_data.get('force_send', False):
            self.instance.send_mail()

        return instance


class MailAdmin(admin.ModelAdmin):
    raw_id_fields = ['sender', ]
    form = MailAdminForm


def register(app_fullname, admins, ignore_models=[]):
    app_label = app_fullname.split('.')[-2:][0]
    for n, model in apps.get_app_config(app_label).models.items():
        if model.__name__ in ignore_models:
            continue
        name = "%sAdmin" % model.__name__
        admin_class = admins.get(name, None)
        if admin_class is None:
            admin_class = type(
                "%sAdmin" % model.__name__,
                (admin.ModelAdmin,), {},
            )

        if admin_class.list_display == ('__str__',):
            excludes = getattr(admin_class, 'list_excludes', ())
            additionals = getattr(admin_class, 'list_additionals', ())
            admin_class.list_display = tuple(
                [f.name for f in model._meta.fields
                 if f.name not in excludes]) + additionals

        admin.site.register(model, admin_class)


register(__name__, globals())
