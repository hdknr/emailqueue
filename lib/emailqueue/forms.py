''' Forms for emailsmtp
'''
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminSplitDateTime
from django.contrib.admin.templatetags.admin_static import static
from django.utils.translation import (
    ugettext_lazy as _,
)
from django.utils.timezone import now

import re


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
    ''' Send Mail Form '''

    recipients = forms.CharField(
        required=False,
        label=_('Recipients'),
        widget=forms.Textarea,
    )

    is_test = forms.BooleanField(
        required=True, initial=True,
        label=_('Is Testing Mail'),
        help_text=_('Is Tesing Mail Help'),)
    ''' Send as Testing(=True) or Live(=False) '''

    due_at = forms.SplitDateTimeField(
        required=False,
        label=_('Scheduled DateTime to send'),
        widget=AdminSplitDateTime,)

    @property
    def admin_media(self):
        return admin_media()

    def get_recipients(self):
        ''' <textarea> may include en email for each line. '''
        return re.findall(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
            self.cleaned_data['recipients'], re.MULTILINE)

    def send_mail(self, mail_obj):
        ''' Send a  :ref:`emailqueue.models.Mail` '''
        due_at = self.cleaned_data['due_at'] or now()
        # is_test = self.cleaned_data['is_test']

        # if send_at is None, send now. Otherwise, later.
        mail_obj.sender.server.handler.send_mail(
            mail_obj, self.get_recipients(), due_at)
