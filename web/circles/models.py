from django.db import models
from emailqueue.models import Mail
from alumni.models import Alumnus
from django.utils.translation import ugettext_lazy as _
# Create your models here.


class Circle(models.Model):
    name = models.CharField(
        _('Circle Name'), max_length=50)

    def __unicode__(self):
        return self.name


class CircleMember(models.Model):
    circle = models.ForeignKey(Circle)
    alumnus = models.ForeignKey(Alumnus)

    def __unicode__(self):
        return self.alumnus.__unicode__()


class CircleLetter(Mail):
    circle = models.ForeignKey(Circle)
