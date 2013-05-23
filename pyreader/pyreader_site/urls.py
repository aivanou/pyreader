from django.conf.urls import url,patterns,include

from pyreader_site import views

urlpatterns=patterns('',
    	url(r'^$',views.index,name='index'),
    	url(r'^test/$',views.test,name='test'),
    	url(r'^login/$',views.login_view,name='login'),
		url(r'^channel/create/$',views.create_channel,name='create_channel'),
		url(r'^channel/show/$',views.show_channels,name='show_channels'),
    	url(r'^channel/(?P<channel_id>\d+)/$',views.channel_details,name='channel_details'),
	)