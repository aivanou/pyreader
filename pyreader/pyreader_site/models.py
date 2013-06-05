from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import get_user_model


class RssChannel(models.Model):
	link=models.CharField(max_length=255,unique=True)
	title=models.CharField(max_length=256,blank=False)
	description=models.CharField(max_length=2048,blank=True)
	creation_date=models.DateTimeField("creation date",default=timezone.now())
	last_update=models.DateTimeField("last update date",default=timezone.now())
	language=models.CharField(max_length=32,default='en')
	copyright=models.CharField(max_length=1024,blank=True)
	#time to live in minutes
	ttl=models.IntegerField(default=30)

	def __unicode__(self):
		return self.title

	class Meta:
		db_table='rss_channels'

class RssItem(models.Model):
	title=models.CharField(max_length=255)
	description=models.CharField(max_length=8096)
	link=models.CharField(max_length=512)
	guid=models.CharField(max_length=512,blank=True)
	pubDate=models.DateTimeField('publication date',default=timezone.now())

	rssChannel=models.ForeignKey(RssChannel)

	class Meta:
		db_table='rss_items'


class ChannelTag(models.Model):
	tag_name=models.CharField(max_length=512,default='default tag name')
	creation_date=models.DateTimeField("tag creation date",default=timezone.now())
	tag_type=models.CharField(max_length=128,default='default tag type')

	def __unicode__(self):
		return self.tag_name

	class Meta:
		db_table='channel_tags'



class Subscription(models.Model):
	user=models.ForeignKey(settings.AUTH_USER_MODEL)
	channel=models.ForeignKey('Channel')
	subs_date=models.DateTimeField('subscription date',default=timezone.now())
	last_update=models.DateTimeField('last subscriprion update',default=timezone.now())

	class Meta:
		db_table='channel_subscription'

class Channel(models.Model):
	title=models.CharField(max_length=255,unique=True)
	ctype=models.CharField(max_length=128,default='public') #private,public
	#specifies who created this channel(user,admin,machine)
	creation_type=models.CharField(max_length=128,default='admin')
	is_category_channel=models.BooleanField(default=False)
	description=models.CharField(max_length=512,blank=True)
	creation_date=models.DateTimeField("creation date",default=timezone.now())
	last_update=models.DateTimeField("last channel update date",default=timezone.now())

	users=models.ManyToManyField(settings.AUTH_USER_MODEL,through='Subscription')
	tags=models.ManyToManyField(ChannelTag)
	rss_channels=models.ManyToManyField(RssChannel)
	sub_channels=models.ManyToManyField('self',symmetrical=False)

	def __unicode__(self):
		return "%s"%(self.title)

	class Meta:
		db_table='channels'