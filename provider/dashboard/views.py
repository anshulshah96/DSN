# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,render_to_response
from django.http import HttpResponse
# Create your views here.
def index(request):
	contract_address = 'http://172.25.12.128:8900/contract'
	return render_to_response("provider/index.html",context={'contract_address': contract_address})