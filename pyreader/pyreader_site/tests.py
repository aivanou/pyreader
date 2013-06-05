"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test import Client
from django.utils import simplejson

from pyreader_site.models import *


class ChannelTest(TestCase):

	fixtures=['data.xml']

	def testChannelCount(self):
		ch_count=Channel.objects.all().count()
		self.assertEqual(ch_count,13)

	def testUserChannels(self):
		ch_count=Channel.objects.filter(users__id=2).count()
		self.assertEquals(ch_count,5)

	def testUserChannelsType(self):
		channels=Channel.objects.filter(users__id=2)
		for channel in channels:
			self.assertEquals(channel.ctype,'private')
			self.assertEquals(channel.users.count(),1)

	def testPublicChannels(self):
		channels=Channel.objects.filter(ctype='public')
		for channel in channels:
			self.assertEquals(channel.users.count(),0)

class RssUrlsTest(TestCase):
	
	fixtures=['data.xml']

	def testChannelRss(self):
		urlsCount=Rss_Url.objects.filter(channel__name='bbc news').count()
		self.assertEquals(urlsCount,2)

class ViewsTest(TestCase):

	fixtures=['data.xml']

	def testIndexAnonymous(self):

		client=Client()
		response=client.get('/')

		categories=response.context['categories']
		self.assertEquals(len(categories),2)

		self.assertEquals(len(categories[0]['channels']),4)

	def testIndexAnonymousWithParameters(self):

		client=Client()
		response=client.get('/?channel_id=1&ctype=public')

		rss_content=response.context[-1]['rss_content']
		self.assertEquals(len(rss_content),10)

	def testInderAnonymousPagination(self):

		client=Client()
		rssDict=simplejson.loads(client.post('/index_page/',
						{'elements':10,'channel_id':1,'ctype':'public'}).content)
		self.assertEquals(len(rssDict),10)

		rssDict=simplejson.loads(client.post('/index_page/',
						{'elements':12,'channel_id':1,'ctype':'public'}).content)
		self.assertEquals(len(rssDict),0)

		rssDict=simplejson.loads(client.post('/index_page/',
						{'elements':10,'channel_id':14,'ctype':'public'}).content)
		self.assertEquals(len(rssDict),0)


	def testIndexLogged(self):
		client=Client()
		self.assertEquals(client.login(username='alex',password='1'),True)

		response=client.get('/')
		categories=response.context['categories']
		self.assertEquals(len(categories),3)

	def testIndexLoggedWithParameters(self):
		client=Client()
		self.assertEquals(client.login(username='alex',password='1'),True)

		response=client.get('/?channel_id=14&ctype=private')

		rss_content=response.context[-1]['rss_content']
		self.assertEquals(len(rss_content),0)



