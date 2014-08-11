from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^jpy_compare/$', 'mfinvest.views.japan_compare_view'),
    url(r'^fund_jpy/$', 'mfinvest.views.mf_japan_view'),

    url(r'^add_trade/$', 'mfinvest.views.add_my_trade'),

    url(r'^add_sample/$', 'mfinvest.views.add_sample'),
    url(r'^$', 'mfinvest.views.default_view'),

)