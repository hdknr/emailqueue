from django.conf.urls import patterns, url
import views


urlpatterns = patterns(
    '',
    url(r'(?P<path>.*)', views.publish, name="docs_publish"),
)
