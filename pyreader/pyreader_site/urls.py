from django.conf.urls import url,patterns,include

from pyreader_site import views

urlpatterns=patterns('',
    	url(r'^$',views.index,name='index'),
        url(r'^index_page/$',views.page_index,name='page_index'),
    	url(r'^test/$',views.test,name='test'),
    	url(r'^accounts/login/$',views.login_view,name='login'),
    	url(r'^accounts/register/$',views.register,name='register'),
    	url(r'^accounts/logout/$',views.logout_view,name='logout'),
        url(r'^channels/$',views.show_channels,name='show_channels'),
		url(r'^channels/create/$',views.create_channel,name='create_channel'),
		url(r'^channels/check_create_channel/$',views.check_create_channel,name='check_create_channel'),
    	url(r'^channels/(?P<channel_id>\d+)/$',views.channel_details,name='channel_details'),
	)