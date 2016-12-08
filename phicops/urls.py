from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    #url(r'^admin/', include(admin.site.urls)),
    url(r'^fc/', include('fundclear.urls')),
    url(r'^fc2/', include('fundclear2.urls')),
    url(r'^fr/', include('fundcodereader.urls')),
    url(r'^bot/', include('bankoftaiwan.urls')),
    url(r'^bot2/', include('bankoftaiwan2.urls')),
    url(r'^mf/', include('mfinvest.urls')),
    url(r'^gi/', include('goldinvest.urls')),
    url(r'^bis/', include('bis_org.urls')),
    url(r'^tg/', include('treasury_gov.urls')),
    url(r'^ir/', include('indexreview.urls')),
    url(r'^twse/', include('twse_gae.urls')),
    url(r'^fetch/', include('urlfetch_gae.urls')),
    
    # Examples:
    # url(r'^$', 'phicops.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^print_config/$', 'phicops.views.print_config'),
    url(r'^test_l10n/$', 'phicops.views.test_l10n'),
    url(r'^env/$', 'phicops.views.os_environment_view'),
    url(r'^conf/$', 'phicops.views.django_settings_view'),
    url(r'^$', 'phicops.views.home'),
)
