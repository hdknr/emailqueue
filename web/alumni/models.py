from django.db import models
from emailqueue.models import Contact, Mail
from django.utils.translation import ugettext_lazy as _
# Create your models here.


class Profile(Contact):
    family_name = models.CharField(
        _('Family Name'), max_length=50)
    first_name = models.CharField(
        _('First Name'), max_length=50)


class Alumnus(Profile):
    entered_year = models.IntegerField(_('Entered Year'))
    entered_school = models.CharField(_('Entered School'), max_length=50)
    graduated_year = models.IntegerField(_('Entered Year'))
    graduated_school = models.CharField(_('Entered School'), max_length=50)


class Letter(Mail):
    ''' Mail for All Alumnus'''
    pass
