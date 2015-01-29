from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

     #-> For GAE CRON task
     url(r'^task/stk_cron_update/$', 'twse_gae.tasks_stock.cron_stk_update_taskhandler'),
     url(r'^task/id_cron_update/$', 'twse_gae.tasks_stock.update_model'),

     #-> GAE Task Handler
     url(r'^task/stk_cupdate/$', 'twse_gae.tasks_stock.cupdate_stk_taskhandler'),
     url(r'^task/stk_update/$', 'twse_gae.tasks_stock.update_stk_taskhandler'),
     url(r'^task/stk_reload/$', 'twse_gae.tasks_stock.reload_stk_task_handler'),
     url(r'^task/id_update/$', 'twse_gae.tasks_stock.update_model_taskhandler'),
          
     #-> STOCK
     url(r'^stock/func/update/$', 'twse_gae.tests_stock.test_stock_update_from_web'),
     url(r'^stock/func/update/(?P<p_type>\w+)/$', 'twse_gae.tests_stock.test_stock_update_from_web'),
     url(r'^stock/func/code_list/$', 'twse_gae.views_stock.code_list_view'),

     #-> TWSE
     url(r'^twse/func/test5/$', 'twse_gae.tests.test_get_index_by_date'),
     url(r'^twse/func/test4/$', 'twse_gae.tests.test_get_last_ym'),
     url(r'^twse/func/test4/(?P<p_stk_no>\w+)/$', 'twse_gae.tests.test_get_last_ym'),
     url(r'^twse/func/test3/$', 'twse_gae.tests.test_get_index_list'),
     url(r'^twse/func/test2/$', 'twse_gae.tests.test_parse_csv_col_date'),
     url(r'^twse/func/test1/$', 'twse_gae.tests.test_get_stock'),
     
     url(r'^twse/func/get_stock/(?P<p_stk_no>\w+)/$', 'twse_gae.tests.test_get_stock'),
     url(r'^twse/func/update_month/(?P<p_stk_no>\w+)/(?P<p_year_month>\w+)/$', 'twse_gae.tests.test_update_month'),
     url(r'^twse/func/get_update_ym/(?P<p_stk_no>\w+)/$', 'twse_gae.tests.test_get_stk_update_ym'),
     
     #-> OTC
     url(r'^otc/func/get_stock/(?P<p_stk_no>\w+)/$', 'twse_gae.tests_otc.func_get_stock'),
     url(r'^otc/func/test/$', 'twse_gae.tests_otc.test'),
     
     #-> General Stock View
     url(r'^(?P<p_stk_no>\w+)/update/$', 'twse_gae.views_stock.menu_update'),

    
)