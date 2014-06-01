from django.conf import settings

class SettingsMiddleware(object):
    def process_request(self, request):
        prefix = request.META.get('SCRIPT_NAME')
        if all([
            prefix,
            not settings.STATIC_URL.startswith(prefix),]):
            settings.STATIC_URL = prefix + settings.STATIC_URL
