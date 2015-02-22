from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
 
     url(r'^task/update/$', 'fundcodereader.tasks.update_codelist'),
     url(r'^task/download/$', 'fundcodereader.tasks.update_fundcode_taskhandler'),

     url(r'^func/test1/$', 'fundcodereader.tests.test_get_codename_list'),
     url(r'^func/test2/$', 'fundcodereader.tests.test_get_fundname'),
     url(r'^func/test3/$', 'fundcodereader.tests.print_content'),

)