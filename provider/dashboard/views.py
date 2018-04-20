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
from dashboard.pos import Pos_provider,Challenge
import json, requests
from background_task import background
from web3 import Web3
from web3.providers.rpc import HTTPProvider
import os

def get_contract():
    r = requests.get(settings.CONTRACT_ADDRESS + "/contract")
    contractAddress = r.json()['address']
    abi = r.json()['abi']
    w3 = Web3(HTTPProvider(settings.RPC_ADDRESS))
    fContract = w3.eth.contract(contractAddress,abi=abi)
    return (w3,fContract)

# @background(schedule=1)
def verify_storage(address,seed,size):
    pos_provider = Pos_provider(seed,size,settings.BASE_DIRECTORY + '/testing')
    pos_provider.setup()

    r = requests.get(settings.CONTRACT_ADDRESS+"/challenge", params = {'adds' : address, 'size' : size})
    challenge = r.json()['challenge']
    print("CHALLENGE : ",challenge)
    solution = pos_provider.prove(Challenge(bytearray.fromhex(challenge)))
    print("SOLUTION : ",solution)
    r = requests.get(settings.CONTRACT_ADDRESS+"/issue", params = {'adds' : address, 'sol' : solution})
    print(r.text)
    try:
        Status.objects.get(address=address).delete()
    except:
        pass

# Create your views here.
def index(request):
    return render_to_response("provider/index.html",context={'base_contract_address': settings.CONTRACT_ADDRESS, 'rpc_address' : settings.RPC_ADDRESS})

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
    status.delete()
    verify_storage(address,seed,int(size))

    return HttpResponse("OKAY")

def status(request):
    return JsonResponse({ 'rate' : settings.PROVIDER_RATE })

def download(request,client,service_num):
    try:
        service = Service.objects.filter(client=client,service_num=service_num)[0]
        print(service.path)
        if os.path.exists(service.path):
            with open(service.path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/bytes")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(service.path)
                return response
        raise Http404
    except Exception as e:
        print(e)
        raise Http404

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.data['name']
            try:
                name = name.split('/')[-1]
            except:
                pass

            handle_uploaded_file(request.FILES['file'],form.data['client'],name)
            web3, contract = get_contract()
            print(form.data)
            contract.functions.createService(int(form.data['size']),settings.PROVIDER_RATE,form.data['client']).transact({'from' : web3.eth.accounts[2],'gas':420000})
            current_count = contract.functions.getProviderServiceCount(web3.eth.accounts[2]).call()
            print("GOT CURRENT COUNT AS : ",current_count)
            Service.objects.create(client=form.data['client'],service_num=current_count,path=settings.BASE_DIRECTORY+'/'+form.data['client']+'/'+name,tag=form.data['tag'],state=form.data['state'])
            return JsonResponse({'service_num' : current_count})
        else:
            print(form.errors)
    else:
        raise Http404

def handle_uploaded_file(f,client,name):
    import os
    cmd = "mkdir -p "+settings.BASE_DIRECTORY+'/'+client+'/'
    os.system(cmd)
    with open(settings.BASE_DIRECTORY+'/'+client+'/'+name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@csrf_exempt
def challenge(request):
    client =request.POST.get('client',None)
    service_num = request.POST.get('servicenum',None)
    challenge = request.POST.get('challenge',None)
    challenge = json.loads(challenge)
    import heartbeat
    # import ipdb
    # ipdb.set_trace()
    service = Service.objects.filter(client=client,service_num=service_num)[0]
    challenge = heartbeat.PySwizzle.Challenge.fromdict(challenge)
    print(service.tag)
    print(service.state)
    tag = heartbeat.PySwizzle.Tag.fromdict(json.loads(service.tag))
    state = heartbeat.PySwizzle.State.fromdict(json.loads(service.state))
    beat = heartbeat.PySwizzle.PySwizzle()
    public_beat = beat.get_public()
    proof = public_beat.prove(open(service.path,'rb'),challenge,tag)
    print(json.dumps(proof.todict()))
    return JsonResponse({'proof' : json.dumps(proof.todict())})