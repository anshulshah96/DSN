from django import forms

class UploadFileForm(forms.Form):
    name = forms.CharField(max_length=50)
    file = forms.FileField()
    client = forms.CharField(max_length=70)