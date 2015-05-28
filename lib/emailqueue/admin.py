from django.contrib import admin
from django.apps import apps


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
