# Create your views here.

from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context,loader
from django.shortcuts import render,get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic
from django import forms
from django.contrib.auth import authenticate,login
from django.utils import timezone
from django.contrib.auth.decorators import login_required

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
	if not request.user.is_authenticated():
		return render(request,'index.html',context)
	else:
		context['username']=request.user.username
		return render(request,'index.html',context)

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
		if not request.GET.get('s_channel',''):
			selected_channel_id=0
		else: 
			selected_channel_id = int(request.GET.get('s_channel',''))
		if selected_channel_id>0:
			selected_channel=get_object_or_404(Channel,pk=selected_channel_id,user_id=user.id)
		else: selected_channel=None
		return render(request,'show_channels.html',{'channels':user_channels,'selected_channel':selected_channel})

@login_required(login_url='/login/')
def channel_details(request,channel_id):
	channel=get_object_or_404(Channel,pk=channel_id,user_id=request.user.id)
	return render(request,'channel.html',{'channel':channel})


def test(request):
	context = {}
	try:
		data = request.POST['text'].strip()
	except:
		context['text'] = 'error'
	else:
		context['text'] = data[::-1]
	return HttpResponse(context)