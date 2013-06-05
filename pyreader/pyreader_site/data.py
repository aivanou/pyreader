from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from pyreader_site.rss_handler import Rss_Handler
from pyreader_site.models import *

def gen_data():
	
	news_ch=Channel(title='news',ctype='public',creation_type='admin',is_category_channel=True)
	ch1=Channel(title="bbc news",description="bbc news")
	ch2=Channel(title='euronews',ctype='public')
	ch3=Channel(title='it channel',ctype='public')
	ch4=Channel(title='all',ctype='public')

	ch11=Channel(title="important channel 1",ctype='private')
	ch12=Channel(title="important channel 2")
	ch13=Channel(title="important channel 3")
	ch14=Channel(title="important channel 4")
	
	url_ch1_1=RssChannel(title='default1',link='http://feeds.bbci.co.uk/news/rss.xml',description='top stories')
	url_ch1_2=RssChannel(title='default2',link='http://feeds.bbci.co.uk/news/world/rss.xml',description='world news')
	url_ch1_3=RssChannel(title='default3',link='http://feeds.bbci.co.uk/news/uk/rss.xml',description='uk news')
	
	url_ch2_1=RssChannel(title='default4',link='http://feeds.feedburner.com/euronews/ru/home?format=xml',description='euronews main')
	url_ch2_2=RssChannel(title='default5',link='http://feeds.feedburner.com/euronews/ru/business?format=xml',description='euronews business')
	
	url_ch3_1=RssChannel(title='default6',link='http://habrahabr.ru/rss/hubs/',description='habrahabr it news')
	url_ch3_2=RssChannel(title='default7',link='http://tech-novelty.ru/feed/')
	url_ch3_3=RssChannel(title='default8',link='http://www.computerweekly.com/rss/All-Computer-Weekly-content.xml')
	
	ch1.save()
	ch2.save()
	ch3.save()
	ch4.save()

	ch11.save()
	ch12.save()
	ch13.save()
	ch14.save()

	news_ch.save()

	news_ch.sub_channels.add(ch1)
	news_ch.sub_channels.add(ch2)
	news_ch.sub_channels.add(ch3)

	user=User.objects.get(username='alex')

	s1=Subscription(user=user,channel=ch1)
	s2=Subscription(user=user,channel=ch2)
	s3=Subscription(user=user,channel=ch11)
	s4=Subscription(user=user,channel=ch12)
	s5=Subscription(user=user,channel=ch13)
	s6=Subscription(user=user,channel=ch14)

	s1.save()
	s2.save()
	s3.save()
	s4.save()
	s5.save()
	s6.save()

	url_ch1_1.save()
	url_ch1_2.save()
	url_ch1_3.save()
	url_ch2_1.save()
	url_ch2_2.save()
	url_ch3_1.save()
	url_ch3_2.save()
	url_ch3_3.save()

	fill_content(url_ch1_1)
	fill_content(url_ch1_2)
	fill_content(url_ch1_3)
	fill_content(url_ch2_1)
	fill_content(url_ch2_2)
	fill_content(url_ch3_1)
	fill_content(url_ch3_2)
	fill_content(url_ch3_3)

	ch1.rss_channels.add(url_ch1_1)
	ch1.rss_channels.add(url_ch1_2)
	ch1.rss_channels.add(url_ch1_2)

	ch2.rss_channels.add(url_ch2_1)
	ch2.rss_channels.add(url_ch2_2)

	ch3.rss_channels.add(url_ch3_1)
	ch3.rss_channels.add(url_ch3_2)
	ch3.rss_channels.add(url_ch3_1)

	ch4.rss_channels.add(url_ch1_1)
	ch4.rss_channels.add(url_ch1_2)
	ch4.rss_channels.add(url_ch1_2)
	ch4.rss_channels.add(url_ch2_1)
	ch4.rss_channels.add(url_ch2_2)
	ch4.rss_channels.add(url_ch3_1)
	ch4.rss_channels.add(url_ch3_2)
	ch4.rss_channels.add(url_ch3_1)
	
	ch11.rss_channels.add(url_ch1_1)
	ch12.rss_channels.add(url_ch1_1)
	ch13.rss_channels.add(url_ch1_1)
	ch14.rss_channels.add(url_ch1_1)


		

def fill_content(rss_url):
	rss=Rss_Handler()
	cnts=rss.get_feed(rss_url.link)
	for cnt in cnts:
		rss_url.rssitem_set.add(RssItem(title=cnt['title'],
						description=cnt['summary'],link=cnt['link']))