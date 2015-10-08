from django.contrib import admin
from django import template
from django.utils.translation import ugettext_lazy as _
from emailqueue.admin import register
import json
import models


class TopicAdminInline(admin.StackedInline):
    model = models.Topic
    max_num = 3


class SourceAdmin(admin.ModelAdmin):
    list_excludes = ('created_at', )
    list_filter = ('service', )
    inlines = [TopicAdminInline, ]


class NotificationAdmin(admin.ModelAdmin):
    list_excludes = ('created_at', 'headers', )
    list_filter = ('topic', )
    readonly_fields = ('sns_json', 'ses_json', 'headers_json', )

    def sns_json(self, obj):
        return template.Template('''
<pre>
{{ m }}
</pre>
''',).render(template.Context(dict(m=obj.message_object.format())))

    sns_json.short_description = _('SNS Message')
    sns_json.allow_tags = True

    def headers_json(self, obj):
        m = json.dumps(obj.headers_object, indent=2)
        return template.Template('''
<pre>
{{ m }}
</pre>
''',).render(template.Context(dict(m=m)))

    headers_json.short_description = _('SNS Headers')
    headers_json.allow_tags = True

    def ses_json(self, obj):
        return template.Template('''
<pre>
{{ m }}
</pre>
''',).render(template.Context(dict(m=obj.message_object.Message.format())))

    ses_json.short_description = _('SES Message')
    ses_json.allow_tags = True

register(__name__, globals())
