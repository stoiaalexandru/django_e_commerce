from django import forms
from .models import Customer


class CustomerCreationForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    address = forms.CharField()
    phone = forms.CharField()
