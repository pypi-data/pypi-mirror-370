from rest_framework import serializers
from .utils import to_e164
import phonenumbers

class PhoneNumberSerializerField(serializers.CharField):
    def __init__(self, *args, region=None, as_object=False, **kwargs):
        self.region = region
        self.as_object = as_object
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return to_e164(value, self.region)

    def to_representation(self, value):
        if not self.as_object:
            return value
        try:
            num = phonenumbers.parse(value, self.region)
            return {
                "raw": value,
                "international": phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                "national": phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.NATIONAL),
                "region": phonenumbers.region_code_for_number(num),
            }
        except Exception:
            return {"raw": value}
