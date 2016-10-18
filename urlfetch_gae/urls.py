from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

     #-> For GAE CRON task
     url(r'^stk/save/$', 'urlfetch_gae.views.fetch_stock_content'),
     url(r'^stk/parse/$', 'urlfetch_gae.views.parse_stock_info'),

     url(r'^twse/save/$', 'urlfetch_gae.views_twse.save_twse_web_content'),
     url(r'^twse/read/$', 'urlfetch_gae.views_twse.read_twse_web_content'),

     url(r'^tw50/save/$', 'urlfetch_gae.views_tw50.save_tw50_web_content'),
     url(r'^tw50/read/$', 'urlfetch_gae.views_tw50.read_tw50_web_content'),

)