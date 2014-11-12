from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

     url(r'^task/update/$', 'indexreview.tasks.indexreview_fc_update_taskhandler'),
     
     url(r'^func/test/$', 'indexreview.tests.test_update_task'),
    
)

