from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^task/eers_update/$', 'bis_org.views.update_bis_eers_taskhandler'),
    
    url(r'^test/$', 'bis_org.tests.test_get_indices'),
    #url(r'^$', 'bis_org.views.home'),
)
