import phonenumbers

def to_e164(value, region=None):
    try:
        num = phonenumbers.parse(value, region)
        if phonenumbers.is_valid_number(num):
            return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return value
    return value
