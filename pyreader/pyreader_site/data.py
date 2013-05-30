from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from pyreader_site.models import *

def gen_data():
	
	cat1=Category(name="news",ctype="public")
	cat2=Category(name="important channels",ctype="public")


	ch1=Channel(name="bbc news",description="bbc news")
	ch2=Channel(name='euronews')
	ch3=Channel(name='it channel')
	ch4=Channel(name='all')

	ch11=Channel(name="important channel 1")
	ch12=Channel(name="important channel 2")
	ch13=Channel(name="important channel 3")
	ch14=Channel(name="important channel 4")
	
	url_ch1_1=Rss_Url(url='http://feeds.bbci.co.uk/news/rss.xml',description='top stories')
	url_ch1_2=Rss_Url(url='http://feeds.bbci.co.uk/news/world/rss.xml',description='world news')
	url_ch1_3=Rss_Url(url='http://feeds.bbci.co.uk/news/uk/rss.xml',description='uk news')
	
	url_ch2_1=Rss_Url(url='http://feeds.feedburner.com/euronews/ru/home?format=xml',description='euronews main')
	url_ch2_2=Rss_Url(url='http://feeds.feedburner.com/euronews/ru/business?format=xml',description='euronews business')
	
	url_ch3_1=Rss_Url(url='http://habrahabr.ru/rss/hubs/',description='habrahabr it news')
	url_ch3_2=Rss_Url(url='http://tech-novelty.ru/feed/')
	url_ch3_3=Rss_Url(url='http://www.computerweekly.com/rss/All-Computer-Weekly-content.xml')
	
	
	ch1.save()
	ch2.save()
	ch3.save()
	ch4.save()

	ch11.save()
	ch12.save()
	ch13.save()
	ch14.save()
	
	cat1.save()
	cat2.save()

	url_ch1_1.save()
	url_ch1_2.save()
	url_ch1_3.save()
	url_ch2_1.save()
	url_ch2_2.save()
	url_ch3_1.save()
	url_ch3_2.save()
	url_ch3_3.save()
	
	ch1.rss_urls.add(url_ch1_1)
	ch1.rss_urls.add(url_ch1_2)
	ch1.rss_urls.add(url_ch1_2)
	
	ch2.rss_urls.add(url_ch2_1)
	ch2.rss_urls.add(url_ch2_2)
	
	ch3.rss_urls.add(url_ch3_1)
	ch3.rss_urls.add(url_ch3_2)
	ch3.rss_urls.add(url_ch3_1)
	
	ch4.rss_urls.add(url_ch1_1)
	ch4.rss_urls.add(url_ch1_2)
	ch4.rss_urls.add(url_ch1_2)
	ch4.rss_urls.add(url_ch2_1)
	ch4.rss_urls.add(url_ch2_2)
	ch4.rss_urls.add(url_ch3_1)
	ch4.rss_urls.add(url_ch3_2)
	ch4.rss_urls.add(url_ch3_1)

	ch11.rss_urls.add(url_ch1_1)
	ch12.rss_urls.add(url_ch1_1)
	ch13.rss_urls.add(url_ch1_1)
	ch14.rss_urls.add(url_ch1_1)

	cat1.channels.add(ch1)
	cat1.channels.add(ch2)
	cat1.channels.add(ch3)
	cat1.channels.add(ch4)
	
	cat2.channels.add(ch11)
	cat2.channels.add(ch12)
	cat2.channels.add(ch13)
	cat2.channels.add(ch14)
	

	cat1.save()
	cat2.save()