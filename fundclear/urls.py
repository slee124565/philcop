from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^flot/(?P<fund_id>\w+)/$', 'fundclear.views.flot_axes_time_view'),

    url(r'^func/test/$', 'fundclear.views._test_get_sample_value_list'),
)