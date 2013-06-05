#TODO: rss_content design
#TODO: popular channels .. 
#TODO: sources of information

from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context,loader,RequestContext
from django.shortcuts import render,get_object_or_404,render_to_response
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import generic
from django import forms
from django.db import transaction,IntegrityError
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.core.cache import get_cache

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

def get_channel_by_type(channel_id,ctype,user):
	try:
		if ctype=='public':
			return Channel.objects.get(pk=channel_id,ctype=ctype)
		elif not user.is_authenticated():
			return None
		else: return Channel.objects.get(pk=channel_id,users__id=user.id)
	except Channel.DoesNotExist:
		return None

def get_public_categories_with_channels():
	cache=get_cache('default')
	categories=cache.get('categories:public_categories',None)
	if categories==None:
		public_categories=Category.objects.filter(ctype='public').order_by('-last_update')
		categories=[]
		for index in range(len(public_categories)):
			pub_cat=public_categories[index]
			category={'id':index,'name':pub_cat.name,
					  'channels':pub_cat.channels.all().order_by('-last_update')}
			categories.append(category)
		cache.add('categories:public_categories',categories,300)

	return categories


def get_public_categories(request):
	return get_public_categories_with_channels()

def get_public_and_private_categories(request):
	categories=get_public_categories_with_channels()
	cache=get_cache('default')
	user_channels=cache.get('categories:'+request.user.username+'_category',None)
	if user_channels==None:
		user_channels=Channel.objects.filter(users=request.user.id).all().order_by('-last_update')
		cache.add('categories:'+request.user.username+'_category',user_channels)
	categories.append({'id':len(categories),'name':'my channels','channels':user_channels})
	return categories

@transaction.autocommit
def index(request):

	if not request.user.is_authenticated():
		categories=get_public_categories(request)
	else: categories=get_public_and_private_categories(request)
	
	if not 'req' in request.GET or not request.GET['req']=='true':
		return render (request,'index.html',{'login_required':False,'categories':categories,
		                					 'channel':None,'rss_content':None})

	if not 'channel_id' in request.GET or not 'ctype' in request.GET:
		return render (request,'index.html',{'login_required':False,'categories':categories,
		                					 'channel':None,'rss_content':None})

	try:
		channel_id=int(request.GET['channel_id'])
		ctype=request.GET['ctype']
	except ValueError:
		return render (request,'index.html',{'login_required':False,'categories':categories,
		                					 'channel':None,'rss_content':None})

	channel=get_channel_by_type(channel_id,ctype,request.user)
	if channel==None:
		return render(request,'index.html',{'login_required':False,'categories':categories,
				                		 	'channel':None,'rss_content':None})

	cache=get_cache('default')
	if ctype=='public':
		rss_content_key='rss:ch_id'+str(channel_id)
	else: rss_content_key='rss:ch_id'+str(channel_id)+'_'+request.user.username
	rss_content=cache.get(rss_content_key,None)
	if rss_content==None:
		#TODO: cachge, to a more flexible variant, where rss can be mixed using some algorithm
		#how many objects should i cache??
		rss_content=Rss_Content.objects.filter(rss_url__in=Rss_Url.objects.filter(channel=channel_id))[0:100]
		cache.add(rss_content_key,rss_content)

	# just a little stub, will be deleted in future. 
	if(len(rss_content)==0):
		rss_handler=Rss_Handler()
		urls=RssChannel.objects.filter(channel__id=channel_id)
		rss_content=[]
		for rss_urls in urls:
			feed=rss_handler.get_feed(rss_urls.url)
			rss_content+=feed
			for record in feed:
				rc=RssItem(title=record['title'],
						description=record['summary'],link=record['link'])
				rss_urls.rssitem_set.add(rc)
			rss_urls.save()
	return render(request,'index.html',	{'login_required':False,'categories':categories,
				 						 'channel':channel,'rss_content':rss_content[0:10]})
@csrf_exempt
def page_index(request):
	if not request.method=='POST':
		return HttpResponseRedirect('/')
	page_size=10
	max_page=10
	channel_id=request.POST['channel_id']
	elements=request.POST['elements']
	ctype=request.POST['ctype'].strip()
	try:
		channel_id=int(channel_id)
		elements=int(elements)
	except ValueError:
		return render(request,'stub_page.html')
	if channel_id<=0:
		return render(request,'stub_page.html')
	if elements<=0:
		elements=0
	 #if mod!=0 we on the last page
	elif elements%page_size!=0:
		return HttpResponse(simplejson.dumps([]),mimetype='application/javascript')
	page=elements/page_size+1
	#TODO: change in future to a more appropriate solution
	if page>=max_page:
		return HttpResponse(simplejson.dumps([]),mimetype='application/javascript')
	if ctype=='public':
		rss_content_key='rss:ch_id'+str(channel_id)
	else: rss_content_key='rss:ch_id'+str(channel_id)+'_'+request.user.username

	cache=get_cache('default')
	rss_content=cache.get(rss_content_key,None)
	if rss_content==None:
		#take away to the function
		if ctype=='public':
			rss_content=Rss_Content.objects.filter(rss_url__in=Rss_Url.objects.filter(channel=channel_id,channel__ctype=ctype))[0:100]
		elif request.user.is_authenticated():
			rss_content=Rss_Content.objects.filter(rss_url__in=Rss_Url.objects.filter(channel=channel_id,channel__users__id=request.user.id))[0:100]
		else:
			return HttpResponse(simplejson.dumps(out_data),mimetype='application/javascript')

	paginator=Paginator(rss_content,page_size)

	try:
		rss_data=paginator.page(page).object_list
		out_data=[]
		for d in rss_data:
			out_data.append({'title':d.title,'summary':d.summary})
	except PageNotAnInteger:
		out_data=[]
	except EmptyPage:
		out_data=[]
	return HttpResponse(simplejson.dumps(out_data),mimetype='application/javascript')

@transaction.autocommit
def login_view(request):
	if request.user.is_authenticated():
		return render(request,'accounts/register.html',
						{'error_message':'please, logout to login under a user',
						 'allow_login':'False'})
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
	if request.user.is_authenticated():
		return render(request,'accounts/register.html',
						{'error_message':'please, logout to register a new user',
						 'allow_registration':'False'})
	if request.method=='POST':
		form=RegisterForm(request.POST)
		if form.is_valid():
			username=form.cleaned_data['username']
			password=form.cleaned_data['password']
			email=form.cleaned_data['email']
			if(User.objects.filter(username=username)):
				form=RegisterForm()
				return render(request,'register.html',
					{'error_message':'user with this email already exists',
					'form':form,'allow_registration':'True'})
			User.objects.create_user(username,email,password)
			user=authenticate(username=username,password=password)
			login(request,user)
			return HttpResponseRedirect('/')
	else:
		form=RegisterForm()
		return render(request,'accounts/register.html',
			{'form':form,'allow_registration':'True'})


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

@transaction.autocommit
@login_required(login_url='/accounts/login/')
def show_channels(request):
	user=request.user
	user_channels=user.channel_set.all().order_by('-last_update')
	return render(request,'channels/show_channels.html',{'channels':user_channels})

@transaction.autocommit
@login_required(login_url='/accounts/login/')
def check_create_channel(request):
	if not request.method=='POST':
		return render(request,'channels/create_channel.html',{'form':ChannelForm()})
	user=request.user
	channel_name=request.POST["name"] # process as string not as SQL statement
	current_time=timezone.now()
	channel=Channel(name=channel_name,creation_date=current_time,last_update=current_time,ctype="private")
	urls=[]
	error_messages=[]
	for key,value in request.POST.iteritems():
		value=value.strip()
		if key.startswith('rss_url') and not value == '':
			url=parse_url(value)
			if(url==None):
				error_messages.append('incorrect url: '+value)
			else:
				urls.append(url)
	if len(error_messages)!=0 or len(urls)==0:
		return render(request,'channels/create_channel.html',
							 {'form':ChannelForm(),'error_messages':error_messages})

	rss_urls=list(Rss_Url.objects.filter(url__in=urls).all())
	for url in urls:
		if(contains(rss_urls,url)): continue
		try:
			rss_url=Rss_Url.objects.create(url=url,creation_date=current_time,last_update=current_time)
			rss_urls.append(rss_url)
		except IntegrityError:
			rss_urls.append(Rss_Url.objects.get(url=url))
	channel.save()
	for rss_url in rss_urls:
		channel.rss_urls.add(rss_url)
	user.channel_set.add(channel)
	return HttpResponseRedirect('/')

def contains(rss_urls,string_url):
	for rss_url in rss_urls:
		if rss_url.url==string_url:
			return True
	return False

def parse_url(url):
	if '://' in url:
		protocol,url=url.split('://')
	else: protocol='http'
	valid=re.compile("^(\w+\.\w+)"
					 "((\.\w+)|(/\w+)){0,}"
					 "(\?(\w+=\w+\&?){0,}){0,}$"
					)
	match=valid.match(url)
	if match==None:
		return None
	return protocol+"://"+url


@login_required(login_url='/accounts/login/')
def channel_details(request,channel_id):
	channel=get_object_or_404(Channel,pk=channel_id,user_id=request.user.id)
	rss_urls=channel.rss_url_set.all()
	rss_feeds=rss_handler.get_feeds(rss_urls)
	return render(request,'channels/channel_details.html',{'channel':channel,'rss_urls':rss_urls,'feeds':rss_feeds})


def test(request):
	return HttpResponse('context')