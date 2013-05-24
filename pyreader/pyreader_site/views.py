# Create your views here.

from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context,loader,RequestContext
from django.shortcuts import render,get_object_or_404,render_to_response
from django.core.urlresolvers import reverse
from django.views import generic
from django import forms
from django.contrib.auth import authenticate,login
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

from pyreader_site.models import *


class LoginForm(forms.Form):
	username=forms.CharField(max_length=256)
	password=forms.CharField(max_length=512)


class ChannelForm(forms.Form):
	name=forms.CharField(max_length=256)
	creation_date=timezone.now()

def index(request):
	name='alex'
	context={'name':name}
	return render_to_response('index.html', {}, context_instance=RequestContext(request))

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
		return render(request,'login.html',{'form':form})

@login_required(login_url='/login/')
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
		return render(request,'create_channel.html',{'form':form})

@login_required(login_url='/login/')
def show_channels(request):
	user=request.user
	user_channels=user.channel_set.all().order_by('-last_channel_update_date')
	return render(request,'show_channels.html',{'channels':user_channels})


@login_required(login_url='/login/')
def check_create_channel(request):
	if not request.method=='POST':
		return render(request,'create_channel.html',{'form':ChannelForm()})
	user=request.user
	channel_name=request.POST["name"]
	current_time=timezone.now()
	channel=Channel(name=channel_name,creation_date=current_time,
		last_channel_update_date=current_time)
	rss_urls=[]
	for key,value in request.POST.iteritems():
		if key.startswith('rss_url'):
			rss_url=Rss_Url(url=value,creation_date=current_time,
							last_update=current_time, decsription='default')
			rss_urls.append(rss_url)
	user.channel_set.add(channel)
	for rss_url in rss_urls:
		channel.rss_url_set.add(rss_url)
	user.save()
	return HttpResponseRedirect('/channel/show/')


@login_required(login_url='/login/')
def channel_details(request,channel_id):
	channel=get_object_or_404(Channel,pk=channel_id,user_id=request.user.id)
	rss_urls=channel.rss_url_set.all()
	return render(request,'channel.html',{'channel':channel,'rss_urls':rss_urls})


def test(request):
	return HttpResponse('context')