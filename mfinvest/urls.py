from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^jpy_compare/$', 'mfinvest.views.japan_nav_compare_view_2'),
    url(r'^jpy_yoy_compare/$', 'mfinvest.views.japan_yoy_compare_view_2'),
    #url(r'^fund_jpy/$', 'mfinvest.views.mf_japan_view'),
    url(r'^fund_jpy/$', 'mfinvest.views.mf_japan_view_2'),

    #url(r'^fund_review/(?P<fund_id>\w+)/(?P<years>\d+)/$', 'mfinvest.views.fund_review_view'),
    #url(r'^fund_review/$', 'mfinvest.views.fund_review_view_2'),
    url(r'^fund_review/$', 'mfinvest.views.fund_review_view_4'),
    

    #url(r'^add_trade/$', 'mfinvest.views.add_my_trade'),
    #url(r'^add_trade_2/$', 'mfinvest.views.add_my_trade_2'),
    url(r'^add_trade_3/$', 'mfinvest.views.add_my_trade_3'),

    #url(r'^add_sample/$', 'mfinvest.views.add_sample'),
    #url(r'^$', 'mfinvest.views.default_view'),

    url(r'^bb/(?P<p_fund_id>\w+)/$', 'mfinvest.tests.bollinger_band_view'),
    url(r'^bis/$', 'mfinvest.tests.bis_org_view'),
)