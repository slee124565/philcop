from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^fund_jpy/$', 'mfinvest.views.mf_japan_view'),
    url(r'^add_sample/$', 'mfinvest.views.add_sample'),
    url(r'^$', 'mfinvest.views.default_view'),

)