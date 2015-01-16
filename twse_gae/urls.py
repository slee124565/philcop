from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

     url(r'^task/list_update/$', 'twse_gae.tasks.list_update_taskhandler'),
     url(r'^task/reload/$', 'twse_gae.tasks.reload_stk_task_handler'),
     url(r'^task/update/$', 'twse_gae.tasks.update_stk_taskhandler'),
     url(r'^task/cupdate/$', 'twse_gae.tasks.cupdate_stk_taskhandler'),
     
     #url(r'^task/view_scan/$', 'fundclear2.tasks.db_scan_review'),
     #url(r'^task/db_scan/$', 'fundclear2.tasks.db_scan_task'),
     #url(r'^task/db_scan_task/$', 'fundclear2.tasks.db_scan_taskhandler'),

     #url(r'^statistic/$', 'fundclear2.views.datamodel_statistic_report_view'),
     
     #url(r'^view/analysis/$', 'fundclear2.views.fund_analysis_view'),
     #url(r'^view/analysis/(?P<p_key>\w+)/$', 'fundclear2.views.fund_analysis_view'),
     
     url(r'^func/test5/$', 'twse_gae.tests.test_get_index_by_date'),
     url(r'^func/test4/$', 'twse_gae.tests.test_get_last_ym'),
     url(r'^func/test4/(?P<p_stk_no>\w+)/$', 'twse_gae.tests.test_get_last_ym'),
     url(r'^func/test3/$', 'twse_gae.tests.test_get_index_list'),
     url(r'^func/test2/$', 'twse_gae.tests.test_parse_csv_col_date'),
     url(r'^func/test1/$', 'twse_gae.tests.test_get_stock'),
     url(r'^func/get_stock/(?P<p_stk_no>\w+)/$', 'twse_gae.tests.test_get_stock'),
     
    
)