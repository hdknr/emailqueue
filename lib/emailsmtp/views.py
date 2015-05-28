# from django.conf import settings
# from django.http import HttpResponse    # , HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required
# import os
# import mimetypes

from emailqueue.models import Mail
import forms


@staff_member_required
def send_mail(request, id):
    mail = Mail.objects.get(id=id)
    form = forms.SendMailForm(
        data=request.POST or None
    )
    if form.is_valid():
        print form.cleaned_data
        pass

    return TemplateResponse(
        request,
        'admin/emailsmtp/send_mail.html',
        dict(request=request, mail=mail, form=form,)
    )
