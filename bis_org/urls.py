from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^task/eers_update/$', 'bis_org.views.update_bis_eers_taskhandler'),
    

    url(r'^$', 'bis_org.views.default_view'),

    url(r'^test/$', 'bis_org.tests.test_get_indices'),
    url(r'^test2/$', 'bis_org.tests.test_mail_api'),
    url(r'^test3/$', 'bis_org.tests.test_conf'),
)
