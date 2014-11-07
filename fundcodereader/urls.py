from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
 
     url(r'^task/dcode/$', 'fundcodereader.tasks.download_fundcode'),

     url(r'^func/test1/$', 'fundcodereader.tests.test_get_codename_list'),
     url(r'^func/test2/$', 'fundcodereader.tests.test_get_fundname'),

)