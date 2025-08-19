from django import forms
from .validators import PhoneNumberValidator

class PhoneNumberWidget(forms.TextInput):
    input_type = "tel"

class PhoneNumberFormField(forms.CharField):
    def __init__(self, *args, region=None, **kwargs):
        kwargs.setdefault("widget", PhoneNumberWidget)
        kwargs.setdefault("validators", [PhoneNumberValidator(region=region)])
        super().__init__(*args, **kwargs)
