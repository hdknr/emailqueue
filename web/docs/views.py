# from django.conf import settings
from django.http import HttpResponse    # , HttpResponseRedirect
# from django.template.response import TemplateResponse
from django.core.files import File
from django.contrib.auth.decorators import login_required
import os
import mimetypes


def _path(path):
    return os.path.join(
        os.path.dirname(__file__),
        os.path.join('build/html/', path))


def publish(request, path):
    if path == '' or path.endswith('/'):
        path = path + "index.html"

    abspath = _path(path)
    mt, dmy = mimetypes.guess_type(abspath)
    return HttpResponse(
        File(open(abspath)), content_type=mt)


@login_required
def protected(request, path):
    return publish(request, path)


def public(request, path):
    return publish(request, path)
