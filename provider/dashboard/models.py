# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Status(models.Model):
	address = models.CharField(unique=True,max_length=70)
	generated = models.BooleanField(default=False)