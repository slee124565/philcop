from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

     url(r'^task/fc_init/$', 'indexreview.tasks.fc2_review_update'),
     url(r'^task/fc_cupdate/$', 'indexreview.tasks.fc2_review_cupdate_taskhandler'),
     url(r'^task/fc_update/$', 'indexreview.tasks.fc2_review_update_taskhandler'),
     
     url(r'^func/test/$', 'indexreview.tests.test_update_task'),
    
)

