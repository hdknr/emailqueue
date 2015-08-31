from django.conf.urls import patterns, url
import views


urlpatterns = patterns(
    '',
    url(r'send_mail/(?P<id>.+)',
        views.send_mail, name="emailqueue_send_mail"),
)
