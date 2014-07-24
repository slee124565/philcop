from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    #url(r'^admin/', include(admin.site.urls)),
    url(r'^fundclear/', include('fundclear.urls')),
    url(r'^bot/', include('bankoftaiwan.urls')),
    
    # Examples:
    # url(r'^$', 'phicops.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'phicops.views.default_view'),
)
