from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

     url(r'^task/init/$', 'fundclear2.tasks.funddata_init'),
     url(r'^task/update/$', 'fundclear2.tasks.funddata_update'),
     url(r'^task/dupdate/$', 'fundclear2.tasks.update_funddata_taskhandler'),
     url(r'^task/cupdate/$', 'fundclear2.tasks.chain_update_taskhandler'),

     url(r'^statistic/$', 'fundclear2.views.datamodel_statistic_report_view'),
     
     url(r'^func/test6/$', 'fundclear2.tests.test_load_all_nav'),
     url(r'^func/test5/$', 'fundclear2.tests.test_get_nav_by_date'),
     url(r'^func/test4/$', 'fundclear2.tests.test_get_value_list'),
     url(r'^func/test3/$', 'fundclear2.tests.test_load_year_nav'),
     url(r'^func/test2/$', 'fundclear2.tests.test_get_fund'),
     url(r'^func/test1/$', 'fundclear2.tests.test_update_from_web'),
     
    
)