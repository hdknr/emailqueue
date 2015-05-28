from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminSplitDateTime
from django.contrib.admin.templatetags.admin_static import static
from django.utils.translation import (
    ugettext_lazy as _,
)


def admin_media():
    extra = '' if settings.DEBUG else '.min'
    js = [
        'core.js',
        'admin/RelatedObjectLookups.js',
        'jquery%s.js' % extra,
        'jquery.init.js',
        'actions%s.js' % extra,
        'urlify.js',
        'prepopulate%s.js' % extra,
    ]

    return forms.Media(
        js=[static('admin/js/%s' % url) for url in js])


class SendMailForm(forms.Form):
    recipients = forms.CharField(
        required=False,
        label=_('Recipients'),
        widget=forms.Textarea,
    )
    is_test = forms.BooleanField(
        required=True, initial=True,
        label=_('Is Testing Mail'),)

    send_at = forms.SplitDateTimeField(
        required=False,
        label=_('Scheduled DateTime to send'),
        widget=AdminSplitDateTime,)

    @property
    def admin_media(self):
        return admin_media()
