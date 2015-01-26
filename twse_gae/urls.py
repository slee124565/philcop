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
     
     
     
     url(r'^stock/task/update/$', 'twse_gae.tasks_stock.update_model'),
     url(r'^stock/task/update_task/$', 'twse_gae.tasks_stock.update_model_taskhandler'),

     url(r'^stock/func/update/$', 'twse_gae.tests_stock.test_stock_update_from_web'),
     url(r'^stock/func/update/(?P<p_type>\w+)/$', 'twse_gae.tests_stock.test_stock_update_from_web'),
     url(r'^stock/func/code_list/$', 'twse_gae.views_stock.code_list_view'),
     
     url(r'^twse/func/test5/$', 'twse_gae.tests.test_get_index_by_date'),
     url(r'^twse/func/test4/$', 'twse_gae.tests.test_get_last_ym'),
     url(r'^twse/func/test4/(?P<p_stk_no>\w+)/$', 'twse_gae.tests.test_get_last_ym'),
     url(r'^twse/func/test3/$', 'twse_gae.tests.test_get_index_list'),
     url(r'^twse/func/test2/$', 'twse_gae.tests.test_parse_csv_col_date'),
     url(r'^twse/func/test1/$', 'twse_gae.tests.test_get_stock'),
     
     url(r'^twse/func/get_stock/(?P<p_stk_no>\w+)/$', 'twse_gae.tests.test_get_stock'),
     url(r'^twse/func/update_month/(?P<p_stk_no>\w+)/(?P<p_year_month>\w+)/$', 'twse_gae.tests.test_update_month'),
     url(r'^twse/func/get_update_ym/(?P<p_stk_no>\w+)/$', 'twse_gae.tests.test_get_stk_update_ym'),
     
     
    
)