from django.conf.urls import url
import views


urlpatterns = [
    url(r'bounce', views.bounce, name='emailses_bounce'),
    url(r'complaint', views.complaint, name='emailses_complaint'),
    url(r'delivery', views.delivery, name='emailses_delivery'),
]
