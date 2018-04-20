from django import forms

class UploadFileForm(forms.Form):
	name = forms.CharField(max_length=50)
	file = forms.FileField()
	client = forms.CharField(max_length=70)
	tag = forms.CharField(max_length=60000)
	state = forms.CharField(max_length=60000)
	size = forms.IntegerField()