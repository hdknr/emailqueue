from django.db import models
from django.utils.translation import ugettext_lazy as _

from emailqueue.models import BaseModel


class Domain(BaseModel):
    '''Domain:

    - used for :ref:`postfix.relay_domains`, :ref:`postfix.transport_maps`
    '''
    domain = models.CharField(
        _('Domain'), max_length=50, unique=True, db_index=True,)
    '''`where_field`, also `select_field` for relay_domains '''

    transport = models.CharField(
        _('Transport'), max_length=200)
    '''`where_field` for transport_maps'''

    alias_domain = models.ForeignKey(
        'Domain', verbose_name=_('Alias Transport'),
        related_name='alias_domain_set',
        null=True, default=None, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _('Domain')
        verbose_name_plural = _('Domain')

    def __unicode__(self):
        return self.domain

    def create_alias_domain(self, name):
        domain, created = Domain.objects.get_or_create(
            doamin=name, transport='error',
            alias=self)
        return domain

    def add_alias_address(self, user, alias_user=None):
        if not self.alias_domain:
            return
        src = '{0}@{1}'.format(user, self.domain)
        dst = '{0}@{1}'.format(alias_user or user, self.alias_domain.domain)
        alias = self.alias_set.filter(recipient=src).first()
        if alias:
            alias.forward = dst
            alias.save()
        else:
            alias = self.alias_set.create(recipient=src, forward=dst)
        return alias


class Alias(BaseModel):
    '''Alias

    - Used in :ref:`postfix.virtual_alias_maps`
    '''
    domain = models.ForeignKey(
        Domain,
        null=True, default=None, blank=True, on_delete=models.SET_NULL)

    recipient = models.EmailField(
        _('Recipient Address'), max_length=100, unique=True, db_index=True)
    '''`where_field` for virtual_alias_maps '''

    forward = models.EmailField(
        _('Forward Address'), max_length=100)
    '''`select_field` for virtual_alias_maps '''

    class Meta:
        verbose_name = _('Alias')
        verbose_name_plural = _('Alias')

    def __unicode__(self):
        return u"{0}>{1}".format(self.recipient, self.forward)
