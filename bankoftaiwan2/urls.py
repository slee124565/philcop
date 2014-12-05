from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^task/init_ex_db/$', 'bankoftaiwan2.tasks.init_ex_taskhandler'),
    url(r'^task/update_ex_db/$', 'bankoftaiwan2.tasks.update_ex_taskhandler'),
    url(r'^task/ex_cupdate/$', 'bankoftaiwan2.tasks.ex_chain_update_taskhandler'),
    
    url(r'^func/test1/$', 'bankoftaiwan2.tests.test_update_from_web'),
    url(r'^func/test2/$', 'bankoftaiwan2.tests.test_get_data_dict'),
    url(r'^func/test3/$', 'bankoftaiwan2.tests.test_get_exchange'),
    url(r'^func/test4/$', 'bankoftaiwan2.tests.test_get_rate'),
    url(r'^func/test5/$', 'bankoftaiwan2.tests.test_get_sample_value_list'),
    url(r'^func/test6/$', 'bankoftaiwan2.tests.test_get_exchange_list'),

)