from __future__ import unicode_literals

from django.conf.urls import url

from django_business_rules.views import BusinessRuleFormView, BusinessRuleListView
from django.contrib.admin.views.decorators import staff_member_required


app_name = 'django_business_rules'
urlpatterns = [
    url(r'^business-rule/$', staff_member_required(BusinessRuleListView.as_view()),
        name='business-rule-list'),
    url(r'^business-rule/(?P<pk>[0-9]+)/$',
        staff_member_required(BusinessRuleFormView.as_view()), name='business-rule-form'),
]
