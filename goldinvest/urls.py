from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^add_trade/$', 'goldinvest.views.add_my_trade'),

    url(r'^$', 'goldinvest.views.default_view'),

)