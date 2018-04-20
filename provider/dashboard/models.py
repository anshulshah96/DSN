# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Status(models.Model):
	address = models.CharField(unique=True,max_length=70)
	generated = models.BooleanField(default=False)

class Service(models.Model):
	client = models.CharField(max_length=70)
	service_num = models.IntegerField(default=0)
	path = models.CharField(max_length=60000)
	tag = models.CharField(max_length=60000)
	state = models.CharField(max_length=60000)