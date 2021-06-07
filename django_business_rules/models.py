from django.db import models

from django.urls import reverse
from django.utils.translation import ugettext_lazy as __
from django_business_rules.model_mixins import SoftDeleteAbstractMixin


class BusinessRuleModel(SoftDeleteAbstractMixin):
    name = models.CharField(
        unique=True, verbose_name=__('name'), max_length=150)
    description = models.TextField(blank=True, verbose_name=__('description'))
    rule_data = models.TextField(verbose_name=__('rule data'))
    rules = models.TextField(verbose_name=__('rules'), default={})

    def get_absolute_url(self):
        return reverse('django_business_rules:business-rule-form',
                       kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
