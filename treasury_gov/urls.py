from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    #url(r'^task/web_update/$', 'treasury_got.views.update_bis_eers_taskhandler'),
    
    url(r'^test/$', 'treasury_gov.tests.test_update_from_web'),
    #url(r'^$', 'bis_org.views.home'),
)
