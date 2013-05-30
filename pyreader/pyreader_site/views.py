# Create your views here.

from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context,loader,RequestContext
from django.shortcuts import render,get_object_or_404,render_to_response
from django.core.urlresolvers import reverse
from django.views import generic
from django import forms
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

import re

from pyreader_site.models import *
from pyreader_site.rss_handler import Rss_Handler

rss_handler=Rss_Handler()

# public_user=User.objects.get(username="public_channels")

class LoginForm(forms.Form):
	username=forms.CharField(max_length=256)
	password=forms.CharField(max_length=512)

class ChannelForm(forms.Form):
	name=forms.CharField(max_length=256)
	creation_date=timezone.now()

class RegisterForm(forms.Form):
	username=forms.CharField(max_length=256)
	email=forms.CharField(max_length=256)
	password=forms.CharField(max_length=256)

def index(request):

	public_categories=Category.objects.filter(ctype='public').order_by('-last_update')[:5]

	categories=[]
	index=0
	for c in public_categories:
		index+=1
		category={}
		category['id']=index
		category['name']=c.name
		category['channels']=c.channels.all().order_by('-last_update')
		categories.append(category)

	if not 'channel_id' in request.GET:
		channel=None
		rss_content=None
	else: 
		channel=Channel.objects.get(pk=request.GET['channel_id'])
		rss_content=rss_handler.get_feeds(channel.rss_urls.all())
	return render(request,'index.html',
					{'login_required':False,'categories':categories,
					 'channel':channel,'rss_content':rss_content})

def login_view(request):
	if request.method == 'POST':
		form=LoginForm(request.POST)
		if form.is_valid():
			user=authenticate(username=form.cleaned_data['username'],
							  password=form.cleaned_data['password'])
			if user is None:
				form=LoginForm()
				return render(request,'login.html',{'error_message':'user none','form':form})
			elif not user.is_active:
				form=LoginForm()
				return render(request,'login.html',{'error_message':'user not active','form':form})
			else:
				login(request,user)
				return HttpResponseRedirect('/')
		else: 
			form=LoginForm()
			return render(request,'login.html',{'error_message':'invalid input data','form':form})
	elif request.method == 'GET':
		form=LoginForm()
		return render(request,'accounts/login.html',{'form':form})

@login_required(login_url='/accounts/login/')
def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')

def register(request):
	if request.method=='POST':
		form=RegisterForm(request.POST)
		if form.is_valid():
			username=form.cleaned_data['username']
			password=form.cleaned_data['password']
			email=form.cleaned_data['email']
			if(User.objects.filter(username=username)):
				form=RegisterForm()
				return render(request,'register.html',{'error_message':'user withi this email already exists','form':form})
			User.objects.create_user(username,email,password)
			user=authenticate(username=username,password=password)
			login(request,user)
			return HttpResponseRedirect('/')
	else:
		form=RegisterForm()
		return render(request,'accounts/register.html',{'form':form})


@login_required(login_url='/accounts/login/')
def create_channel(request):
	if request.method == 'POST':
		form=ChannelForm(request.POST)
		if form.is_valid():
			channel_name=form.cleaned_data['name']
			creation_date=form.creation_date
			last_update_date=creation_date
			ch=Channel(name=channel_name,creation_date=creation_date,
					   last_channel_update_date=last_update_date)
			ch.user=request.user
			ch.save()
			return HttpResponseRedirect('/channel/show/')
	elif request.method=='GET':
		form=ChannelForm()
		return render(request,'channels/create_channel.html',{'form':form})

@login_required(login_url='/accounts/login/')
def show_channels(request):
	user=request.user
	user_channels=user.channel_set.all().order_by('-last_channel_update_date')
	return render(request,'channels/show_channels.html',{'channels':user_channels})


@login_required(login_url='/accounts/login/')
def check_create_channel(request):
	if not request.method=='POST':
		return render(request,'channels/create_channel.html',{'form':ChannelForm()})
	user=request.user
	channel_name=request.POST["name"]
	current_time=timezone.now()
	channel=Channel(name=channel_name,creation_date=current_time,
		last_channel_update_date=current_time)
	rss_urls=[]
	error_messages=[]
	for key,value in request.POST.iteritems():
		value=value.strip()
		if key.startswith('rss_url') and not value == '':
			url=check_url(value)
			if(url==False):
				error_messages.append('incorrect url: '+value)
			else:
				rss_url=Rss_Url(url=value,creation_date=current_time,
								last_update=current_time, decsription='default')
				rss_urls.append(rss_url)
	if len(error_messages)!=0 or len(rss_urls)==0:
		return render(request,'channels/create_channel.html',{'form':ChannelForm(),'error_messages':error_messages})
	user.channel_set.add(channel)
	for rss_url in rss_urls:
		channel.rss_url_set.add(rss_url)
	user.save()
	return HttpResponseRedirect('/')

def check_url(url):
	if '://' in url:
		protocol,url=url.split('://')[0]
	else: protocol='http'
	valid=re.compile("^(\w+\.\w+)"
					 "((\.\w+)|(/\w+)){0,}"
					 "(\?(\w+=\w+\&?){0,}){0,}$"
					)
	match=valid.match(url)
	if match==None:
		return False
	return protocol+"://"+url


@login_required(login_url='/accounts/login/')
def channel_details(request,channel_id):
	channel=get_object_or_404(Channel,pk=channel_id,user_id=request.user.id)
	rss_urls=channel.rss_url_set.all()
	rss_feeds=rss_handler.get_feeds(rss_urls)
	return render(request,'channels/channel_details.html',{'channel':channel,'rss_urls':rss_urls,'feeds':rss_feeds})


def test(request):
	return HttpResponse('context')