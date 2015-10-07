# from django.contrib import admin
# from django.utils.translation import ugettext_lazy as _
from emailqueue.admin import register


register(__name__, globals())
