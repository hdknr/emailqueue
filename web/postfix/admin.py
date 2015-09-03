from django.contrib import admin
from emailqueue.admin import register


class AliasAdmin(admin.ModelAdmin):
    list_filter = ('domain', )
    search_fields = ('recipient', 'forward', )

register(__name__, globals())
