from django.contrib import admin
from django.apps import apps
from django.utils.translation import ugettext_lazy as _
from django import template, forms
from django.utils.safestring import mark_safe as _S
from django.core.urlresolvers import reverse

from djuploader.models import UploadModel

import models


def _T(src, **ctx):
    return _S(template.Template(src).render(template.Context(ctx)))


def model_link(model, parent=None):
    url = reverse("admin:{0}_{1}_changelist".format(
        model._meta.app_label,
        model._meta.model_name,
    ))
    if parent:
        r = [i.field.name for i in parent._meta.related_objects
             if i.related_model == model]
        if len(r) > 0:
            url += "?{0}={1}".format(r[0], parent.id)
    # finally returns url
    return url


class MailAddressAdmin(admin.ModelAdmin):
    search_fields = ['email', ]
    list_filter = ('enabled', )
    date_hierarchy = 'updated_at'
    list_excludes = ('created_at', )


class RecipientAdminForm(forms.ModelForm):
    force_reset = forms.BooleanField(
        label=_('Force Reset Recipient'),
        help_text=_('Force Reset Recipient Help'),
        initial=False, required=False)

    class Meta:
        model = models.Recipient
        exclude = ['error_message', 'sent_at', ]

    def save(self, *args, **kwargs):
        if self.cleaned_data.get('force_reset', False):
            self.instance.sent_at = None

        return super(RecipientAdminForm, self).save(*args, **kwargs)


class RecipientAdmin(admin.ModelAdmin):
    raw_id_fields = ['mail', 'to', ]
    date_hierarchy = 'sent_at'
    list_filter = ('to__enabled', )
    list_excludes = ('created_at', )
    list_additionals = ('address_status', )
    form = RecipientAdminForm
    readonly_fields = ('sent_at', 'error_message', )
    actions = ['reset_recipients', ]

    def address_status(self, obj):
        return u"{0}({1})".format(
            obj.to.enabled, obj.to.bounced,
        )

    address_status.short_description = _(u"Address Status")
    address_status.allow_tags = True

    def reset_recipients(self, request, queryset):
        queryset.update(sent_at=None)

    reset_recipients.short_description = _('Reset Recipients')


class PostboxAdmin(admin.ModelAdmin):
    raw_id_fields = ['forward', ]
    list_excludes = ('created_at', )
    list_filter = ('server', 'deleted', )
    search_fields = ('address', 'forward__email', )


class RelayAdmin(admin.ModelAdmin):
    raw_id_fields = ['sender', 'postbox', ]
    list_excludes = ('created_at', )


class ReportAdmin(admin.ModelAdmin):
    raw_id_fields = ['address', 'mail', 'bounce', ]


class MessageAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    actions = ['process_message', ]
    list_filter = ['service', 'server', ]
    list_excludes = ['created_at', 'raw_message', ]

    def process_message(self, request, queryset):
        for instance in queryset:
            if instance.server and instance.server.handler:
                instance.server.handler.process_message(instance)

    process_message.short_description = _('Process Message')


class MailAdminForm(forms.ModelForm):
    force_send = forms.BooleanField(
        label=_('Force Send This Mail'),
        help_text=_('Force Send This Mail Help'),
        initial=False, required=False)

    class Meta:
        model = models.Mail
        exclude = []
        widgets = {
            'status': forms.RadioSelect(),
        }

    def save(self, *args, **kwargs):
        if self.cleaned_data.get('force_send', False):
            self.instance.reset_status()

        instance = super(MailAdminForm, self).save(*args, **kwargs)

        if all([
            self.instance.status == self.instance.STATUS_QUEUED,
            self.instance.sent_at is None,
        ]):
            self.instance.send_mail()

        return instance


class MailAdmin(admin.ModelAdmin):
    raw_id_fields = ['sender', ]
    list_filter = ('status', )
    list_excludes = ('created_at', )
    date_hierarchy = 'sent_at'
    form = MailAdminForm
    readonly_fields = ('sent_at', 'recipients', )

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['upload_model'] = UploadModel.objects.get_or_create(
            content_type=models.Recipient.contenttype(),
            parent_content_type=models.Mail.contenttype(),
        )[0]

        return super(MailAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)

    def recipients(self, obj):
        model = models.Recipient
        link = model_link(model, obj)
        return _T('''<a href="{{ u }}">{{ m.verbose_name }}</a>''',
                  u=link, m=model._meta)

    recipients.short_description = _("Recipeints")
    recipients.allow_tags = True


class MailTemplateAdmin(admin.ModelAdmin):
    raw_id_fields = ['sender', ]


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
