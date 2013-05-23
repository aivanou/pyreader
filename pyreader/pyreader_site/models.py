from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.

#class User(models.Model):
#	username=models.CharField(max_length=63)
#	email=models.CharField(max_length=255)
#	password=models.CharField(max_length=1024)#

#	def __unicode__(self):
#		return "%s:%s"%(self.username,self.email)#

#	class Meta:
#		db_table='users'


class Channel_Tag(models.Model):
	tag_name=models.CharField(max_length=512)
	creation_date=models.DateTimeField("tag creation date")
	tag_type=models.CharField(max_length=128)

	def __unicode__(self):
		return self.tag_name

	class Meta:
		db_table='channel_tags'

class Channel(models.Model):
	user=models.ForeignKey(settings.AUTH_USER_MODEL)
	tags=models.ManyToManyField(Channel_Tag)
	name=models.CharField(max_length=512)
	creation_date=models.DateTimeField("creation date")
	last_channel_update_date=models.DateTimeField("last channel update date")

	def __unicode__(self):
		return "%s"%(self.name)

	class Meta:
		db_table='channels'
		

class Rss_Url(models.Model):
	channel=models.ForeignKey(Channel)
	url=models.CharField(max_length=1024)
	decsription=models.CharField(max_length=2048)
	creation_date=models.DateTimeField("creation date")
	last_update=models.DateTimeField("last update date")

	def __unicode__(self):
		return self.url

	class Meta:
		db_table='rss_urls'



		