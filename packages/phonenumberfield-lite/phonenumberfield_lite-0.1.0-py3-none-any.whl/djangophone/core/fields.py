from django.db import models
from django.conf import settings
from .validators import PhoneNumberValidator
from .utils import to_e164

class PhoneNumberField(models.CharField):
    def __init__(self, *args, region=None, **kwargs):
        self.region = region or getattr(settings, "PHONENUMBERFIELD_DEFAULT_REGION", None)
        kwargs.setdefault("max_length", 32)
        kwargs.setdefault("validators", [PhoneNumberValidator(region=self.region)])
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        return to_e164(value, region=self.region) if value else value

    def from_db_value(self, value, expression, connection):
        return value
