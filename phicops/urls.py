from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    #url(r'^admin/', include(admin.site.urls)),
    url(r'^fc/', include('fundclear.urls')),
    url(r'^bot/', include('bankoftaiwan.urls')),
    url(r'^mf/', include('mfinvest.urls')),
    url(r'^gi/', include('goldinvest.urls')),
    url(r'^bis/', include('bis_org.urls')),
    url(r'^tg/', include('treasury_gov.urls')),
    
    # Examples:
    # url(r'^$', 'phicops.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^print_config/$', 'phicops.views.print_config'),
    url(r'^test_l10n/$', 'phicops.views.test_l10n'),
    url(r'^$', 'phicops.views.home'),
)
