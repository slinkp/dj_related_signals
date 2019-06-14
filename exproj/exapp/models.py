from django.db import models
from django.db.models.signals import (
    pre_save,
    post_save,
    pre_delete,
)
from django.dispatch import receiver

import collections


class Company(models.Model):

    name = models.CharField(max_length=100)


class CustomerCategory(models.Model):

    name = models.CharField(max_length=100)


class Customer(models.Model):

    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, null=True, related_name='customers')

    # With an intermediary
    categories_indirect = models.ManyToManyField(
        CustomerCategory,
        through='CustomerCategoryRel',
        related_name='customers_indirect')

    # Without an intermediary
    categories_direct = models.ManyToManyField(
        CustomerCategory,
        related_name='customers_direct')


class CustomerExtraJunk(models.Model):

    customer = models.OneToOneField(
        Customer, related_name='extrajunk', null=True)


class CustomerCategoryRel(models.Model):

    class Meta:
        unique_together = ("customer", "category")

    customer = models.ForeignKey(Customer)
    category = models.ForeignKey(CustomerCategory)


signal_log = collections.defaultdict(list)


@receiver(pre_save, sender=Company)
def pre_company_save(sender, **kwargs):
    signal_log['company presave'].append((sender, kwargs))


@receiver(pre_save, sender=Customer)
def pre_customer_save(sender, **kwargs):
    signal_log['customer presave'].append((sender, kwargs))


@receiver(pre_save, sender=CustomerCategory)
def pre_category_save(sender, **kwargs):
    signal_log['category presave'].append((sender, kwargs))


@receiver(pre_save, sender=CustomerExtraJunk)
def pre_extrajunk_save(sender, **kwargs):
    signal_log['extra junk presave'].append((sender, kwargs))


@receiver(pre_save, sender=CustomerCategoryRel)
def add_customer_category_rel(sender, **kwargs):
    signal_log['rel presave'].append((sender, kwargs))


@receiver(pre_delete, sender=CustomerCategoryRel)
def remove_customer_category_rel(sender, **kwargs):
    signal_log['rel predelete'].append((sender, kwargs))