"""
DJANGO_IRAN_SMS = {
    'AUTHENTICATION': 'rest_framework_simplejwt',   # rest_framework_simplejwt
    'SMS_BACKEND': 'PARSIAN_WEBCO_IR',              # PARSIAN_WEBCO_IR , MELI_PAYAMAK_COM , KAVENEGAR_COM
    'OTP_CODE': {
        'LENGTH': 8,                                # DEFAULT 8
        'EXPIRE_PER_MINUTES': 4,                    # DEFAULT 4
    },
    'PARSIAN_WEBCO_IR': {
        'API_KEY': '',
        'TEMPLATES': {
            'OTP_CODE': 1,
        }
    },
    'MELI_PAYAMAK_COM': {
        'USERNAME': '',
        'PASSWORD': '',
        'FROM': '',
    },
    'KAVENEGAR_COM': {
        'API_KEY': '656F6635756C485658666F6A52307562456C4F5043714769597A58434D2B527974434534672B50445736553D',
        'FROM': '2000660110'
    }

    ...
}
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SERVICE_NAME = 'DJANGO_IRAN_SMS'

AUTH_SERVICE = {
    'JWT_SIMPLE_DRF': 'rest_framework_simplejwt'
}

SMS_SERVICES = {
    'PARSIAN_WEBCO_IR': 'PARSIAN_WEBCO_IR',
    'MELI_PAYAMAK_COM': 'MELI_PAYAMAK_COM'
}

def init_check():
    try:
        if not hasattr(settings, SERVICE_NAME):
            raise ImproperlyConfigured(f'{SERVICE_NAME} must be defined in settings.py.')
        else:
            auth_service = getattr(settings, SERVICE_NAME).get('AUTHENTICATION')
            if not auth_service:
                raise ImproperlyConfigured(f'AUTHENTICATION kay must be defined in {SERVICE_NAME} for choice sms service provider.')
            sms_service = getattr(settings, SERVICE_NAME).get('SMS_BACKEND')
            if not sms_service:
                raise ImproperlyConfigured(f'SMS_BACKEND key must be defined in {SERVICE_NAME} for get login access to sms provider.')
        return {'AUTHENTICATION': auth_service, 'SMS_BACKEND': sms_service}
    except ImproperlyConfigured as e:
        print(f"Configuration Error: {e}")
        raise
    except:
        pass
    return False

def otp_code_length():
    try:
        otp_len = getattr(settings, SERVICE_NAME, {}).get('OTP_CODE', {}).get('LENGTH', 6)
        if not isinstance(otp_len, int):
            raise ImproperlyConfigured("OTP_CODE LENGTH must be int.")
        if otp_len < 3 or otp_len > 10:
            raise ImproperlyConfigured("OTP_CODE LENGTH must be less than or equal to 10 and greater than or equal to 3.")
        return otp_len
    except ImproperlyConfigured as e:
        print(f"Configuration Error: {e}")
        raise
    except:
        return 6

def otp_code_expire():
    try:
        otp_exp = getattr(settings, SERVICE_NAME, {}).get('OTP_CODE', {}).get('EXPIRE_PER_MINUTES', 2)
        if not isinstance(otp_exp, int):
            raise ImproperlyConfigured("OTP_CODE EXPIRE must be int.")
        if otp_exp <= 0:
            raise ImproperlyConfigured("OTP_CODE EXPIRE must be greater than 0.")
        return otp_exp
    except ImproperlyConfigured as e:
        print(f"Configuration Error: {e}")
        raise
    except:
        return 2


def sms_service_check(sms_service=None):
    try:
        if init_check():
            if sms_service not in settings.DJANGO_IRAN_SMS:
                raise ImproperlyConfigured(f'{sms_service} must be defiend in settings.py -> DJANGO_IRAN_SMS.')
            return True
    except ImproperlyConfigured as e:
        print(f"Configuration Error: {e}")
        raise
    except:
        pass
    return False


