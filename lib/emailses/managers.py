from django.db import models
import methods


class NotificationQuerySet(models.QuerySet):

    def create(self, meta, message, **kwargs):
        kwargs['headers'] = methods.BaseObjectSerializer.dumps(meta)
        return super(NotificationQuerySet, self).create(
            message=message, **kwargs)
