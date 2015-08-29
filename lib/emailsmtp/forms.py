''' Forms for emailsmtp
'''
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminSplitDateTime
from django.contrib.admin.templatetags.admin_static import static
from django.utils.translation import (
    ugettext_lazy as _,
)
import re

import tasks


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

    send_at = forms.SplitDateTimeField(
        required=False,
        label=_('Scheduled DateTime to send'),
        widget=AdminSplitDateTime,)

    @property
    def admin_media(self):
        return admin_media()

    def get_recipients(self):
        return re.findall(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
            self.cleaned_data['recipients'], re.MULTILINE)

    def send_mail(self, mail_obj):
        ''' Send a  :ref:`emailqueue.models.Mail` '''
        send_at = self.cleaned_data['send_at']
        is_test = self.cleaned_data['is_test']
        if is_test:
            if send_at:
                tasks.send_mail_test.apply_async(
                    [mail_obj.id, self.get_recipients()],
                    eta=tasks.make_eta(send_at))
            else:
                tasks.send_mail_test(mail_obj, self.get_recipients())
