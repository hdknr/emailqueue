from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from emailqueue.admin import register


class InboundAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    readonly_fields = ('body_text', )

    def body_text(self, obj):

        def _body(po):
            payload = po.get_payload()
            if isinstance(payload, list):
                # po.is_multipart() == True
                return "<hr/>".join([_body(p) for p in payload])
            if isinstance(payload, basestring):
                cs = po.get_content_charset() or po.get_charset()
                if cs:
                    return unicode(
                        po.get_payload(decode=True), cs, "replace")

                return payload
            return ''

        return _body(obj.mailobject())

    body_text.short_description = _('Body Text')
    body_text.allow_tags = True

register(__name__, globals())
