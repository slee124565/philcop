from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^add_trade/$', 'goldinvest.views.add_my_trade'),

    url(r'^bb/daily/$', 'goldinvest.views.daily_bb_view'),
    url(r'^bb/daily/(?P<p_currency>\w+)/$', 'goldinvest.views.daily_bb_view'),
    url(r'^bb/daily/(?P<p_currency>\w+)/(?P<p_timeframe>\w+)/$', 'goldinvest.views.daily_bb_view'),
    url(r'^bb/daily/(?P<p_currency>\w+)/(?P<p_timeframe>\w+)/(?P<p_sdw>\w+)/$', 'goldinvest.views.daily_bb_view'),
    
    url(r'^bb/weekly/$', 'goldinvest.views.weekly_bb_view'),
    url(r'^bb/weekly/(?P<p_currency>\w+)/$', 'goldinvest.views.weekly_bb_view'),
    url(r'^bb/weekly/(?P<p_currency>\w+)/(?P<p_timeframe>\w+)/$', 'goldinvest.views.weekly_bb_view'),
    url(r'^bb/weekly/(?P<p_currency>\w+)/(?P<p_timeframe>\w+)/(?P<p_sdw>\w+)/$', 'goldinvest.views.weekly_bb_view'),
    
    url(r'^price/$', 'goldinvest.views.price_view'),
    url(r'^price/(?P<p_currency>\w+)/$', 'goldinvest.views.price_view'),
    url(r'^price/(?P<p_currency>\w+)/(?P<p_view_months>\w+)/$', 'goldinvest.views.price_view'),

    url(r'^$', 'goldinvest.views.default_view'),

)