from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^task/update/$', 'treasury_gov.tasks.update_treasury_taskhandler'),
    url(r'^init/$', 'treasury_gov.views.treasury_init_view'), 
    url(r'^check/$', 'treasury_gov.views.datastore_check_view'),
    
    
    #url(r'^test/$', 'treasury_gov.tests.test_get_yield_list_since'),
    #url(r'^test/$', 'treasury_gov.tests.test_get_tenor_list'),
    #url(r'^test/$', 'treasury_gov.tests.test_get_yield_by_date'),
    url(r'^test/$', 'treasury_gov.tests.test_get_yield_list_by_tenor'),
    #url(r'^test/$', 'treasury_gov.tests.test_get_treasury'),
    #url(r'^test/$', 'treasury_gov.tests.test_update_from_web'),
    #url(r'^$', 'bis_org.views.home'),
)
