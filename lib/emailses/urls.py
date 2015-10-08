from django.conf.urls import url
import views


urlpatterns = [
    url(r'(?P<topic>.+)', views.notify, name='emailses_notify'),
]
