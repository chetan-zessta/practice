# forms.py
from django import forms

class JobSearchForm(forms.Form):
    keyword = forms.CharField(required=False)
    location = forms.CharField(required=False)
    experience = forms.CharField(required=False)
