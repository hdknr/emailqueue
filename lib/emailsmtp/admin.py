from django.contrib import admin
from django.apps import apps
from django.utils.translation import ugettext_lazy as _


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


for name, model in apps.get_app_config(
        __name__.split('.')[-2:][0]).models.items():

    name = "%sAdmin" % model.__name__

    admin_class = globals().get(name, None)
    if admin_class is None:
        params = {}
        admin_class = type(
            "%sAdmin" % model.__name__,
            (admin.ModelAdmin,),
            params,
        )

    if admin_class.list_display == ('__str__', ):
        admin_class.list_display = tuple(
            [f.name for f in model._meta.fields])

    admin.site.register(model, admin_class)
