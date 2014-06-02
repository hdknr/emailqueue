from django.contrib import admin
from django.db.models import get_app, get_models
from django.forms import ModelForm
from models import Service
from emailqueue.services.ses import SnsResource


class ServiceAdminForm(ModelForm):

    class Meta:
        model = Service
        exclude = ['notify_uri']


class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = tuple([f.name for f in Service._meta.fields])

    def save_model(self, request, obj, form, change):
        super(ServiceAdmin, self).save_model(request, obj, form, change)
        obj.notify_uri = request.build_absolute_uri(
            obj.service.notify_path()
        )
        obj.save()


for model in get_models(get_app(__name__.split('.')[-2:][0])):

    name = "%sAdmin" % model.__name__

    admin_class = globals().get(name, None)
    if admin_class is None:
        params = dict(
            list_display=tuple([f.name for f in model._meta.fields]),)
        admin_class = type(
            "%sAdmin" % model.__name__,
            (admin.ModelAdmin,),
            params,
        )

    admin.site.register(model, admin_class)
