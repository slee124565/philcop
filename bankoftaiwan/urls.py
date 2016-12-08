from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^exchange/JPY/$', 'bankoftaiwan.views.exchange_jpy_view'),
    url(r'^gold/twd/$', 'bankoftaiwan.views.gold_tw_view'),

)