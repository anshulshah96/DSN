# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from dashboard.models import *

from background_task import background
@background(schedule=1)
def verify_storage(address,seed,size):
	f = open('/home/nikhil96sher/testing','w')
	f.write("VERIFY STORAGE")
	f.close()

# Create your views here.
def index(request):
	return render_to_response("provider/index.html",context={'base_contract_address': settings.CONTRACT_ADDRESS})

def get_status(request,address):
	try:
		Status.objects.get(address=address)
		return HttpResponse("OK")
	except Exception as e:
		print(e)
		raise Http404

@csrf_exempt
def generate_data(request,address):
	status,created = Status.objects.get_or_create(address=address)
	status.generated = False
	status.save()

	seed = request.POST.get('seed',None)
	size = request.POST.get('size',None)
	verify_storage(address,seed,size)

	return HttpResponse("OK")