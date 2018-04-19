# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from dashboard.models import *
from django.http import HttpResponseRedirect
from django.shortcuts import render
from dashboard.forms import UploadFileForm
from django.http import JsonResponse

import json
from background_task import background

@background(schedule=1)
def verify_storage(address,seed,size):
    pos_provider = Pos_provider(seed,size,settings.BASE_DIRECTORY + '/testing')
    pos_provider.setup()

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

def status(request):
    return JsonResponse({ 'rate' : settings.PROVIDER_RATE })

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'],form.data['client'],form.data['name'])
            ## CREATE CONTRACT HERE
            return JsonResponse({'service_num' : 0})
        else:
            print(form.errors)
    else:
        raise Http404

def handle_uploaded_file(f,client,name):
    import os
    try:
        name = name.split('/')[-1]
    except:
        pass
    cmd = "mkdir -p "+settings.BASE_DIRECTORY+'/'+client+'/'
    os.system(cmd)
    with open(settings.BASE_DIRECTORY+'/'+client+'/'+name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)