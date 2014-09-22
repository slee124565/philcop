from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    #url(r'^admin/', include(admin.site.urls)),
    url(r'^fc/', include('fundclear.urls')),
    url(r'^bot/', include('bankoftaiwan.urls')),
    url(r'^mf/', include('mfinvest.urls')),
    
    # Examples:
    # url(r'^$', 'phicops.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^print_config/$', 'phicops.views.print_config'),
    url(r'^$', 'phicops.views.home'),
)
