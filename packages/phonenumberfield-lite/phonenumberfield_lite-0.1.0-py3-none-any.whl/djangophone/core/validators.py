import phonenumbers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class PhoneNumberValidator:
    message = _("Enter a valid phone number.")
    code = "invalid"

    def __init__(self, region=None):
        self.region = region

    def __call__(self, value):
        try:
            num = phonenumbers.parse(value, self.region)
            if not phonenumbers.is_valid_number(num):
                raise ValidationError(self.message, code=self.code)
        except Exception:
            raise ValidationError(self.message, code=self.code)
