from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone


class Rss_Url(models.Model):
	url=models.CharField(max_length=255,unique=True)

	description=models.CharField(max_length=2048,blank=True)
	creation_date=models.DateTimeField("creation date",default=timezone.now())
	last_update=models.DateTimeField("last update date",default=timezone.now())

	def __unicode__(self):
		return self.url

	class Meta:
		db_table='rss_urls'


class Channel_Tag(models.Model):
	tag_name=models.CharField(max_length=512,default='default tag name')
	creation_date=models.DateTimeField("tag creation date",default=timezone.now())
	tag_type=models.CharField(max_length=128,default='default tag type')

	def __unicode__(self):
		return self.tag_name

	class Meta:
		db_table='channel_tags'

class Channel(models.Model):
	users=models.ManyToManyField(settings.AUTH_USER_MODEL)
	tags=models.ManyToManyField(Channel_Tag)
	rss_urls=models.ManyToManyField(Rss_Url)

	name=models.CharField(max_length=255,unique=True)
	ctype=models.CharField(max_length=128,default='public') #private,public
	description=models.CharField(max_length=512,blank=True)
	creation_date=models.DateTimeField("creation date",default=timezone.now())
	last_update=models.DateTimeField("last channel update date",default=timezone.now())

	def __unicode__(self):
		return "%s"%(self.name)

	class Meta:
		db_table='channels'

class Category(models.Model):
	name=models.CharField(max_length=255,unique=True)
	ctype=models.CharField(max_length=128,default='public')
	creation_date=models.DateTimeField(default=timezone.now())
	last_update=models.DateTimeField(default=timezone.now())

	channels=models.ManyToManyField(Channel)

	def __unicode__(self):
		return self.name

	class Meta:
		db_table='categories'
		