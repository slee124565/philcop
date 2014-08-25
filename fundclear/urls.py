from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^task/update/(?P<fund_id>\w+)/$', 'fundclear.tasks.update_taskhandler'),
    url(r'^task/update_test/(?P<fund_id>\w+)/$', 'fundclear.tasks.update_test'),
    url(r'^task/chain_update/$', 'fundclear.tasks.chain_update_taskhandler'),
    url(r'^task/chain_update_test/$', 'fundclear.tasks.chain_update_test'),
    url(r'^task/update_all/$', 'fundclear.tasks.update_all_taskhandler'),

    url(r'^flot/(?P<fund_id>\w+)/$', 'fundclear.views.flot_axes_time_view'),

    url(r'^func/save_fundcode/$', 'fundclear.views.save_fundcode'),
    url(r'^func/review_fundcode/$', 'fundclear.views.review_fundcode_list'),

    #url(r'^func/test/$', 'fundclear.views._test_get_sample_value_list'),
    #url(r'^func/test/$', 'fundclear.views._test_get_fund_code_name'),
    #url(r'^func/test/$', 'fundclear.views._test_get_fund_info_list'),
    #url(r'^func/test/$', 'fundclear.views._test_save_fundcode_config'),
    #url(r'^func/test/$', 'fundclear.views._test_get_fundcode_list'),
    url(r'^func/test/$', 'fundclear.views._test_fundreview_model'),
    
    
    
    
    
)