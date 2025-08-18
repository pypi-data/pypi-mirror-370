"""
DJANGO_CHELSERU = {
    'AUTH': {
        'AUTH_METHOD'       : 'OTP',                        # OTP, PASSWD
        'AUTH_SERVICE'      : 'rest_framework_simplejwt',   # rest_framework_simplejwt
        'OPTIONS': {
            'OTP_LENGTH'            : 8,    # DEFAULT 8
            'OTP_EXPIRE_PER_MINUTES': 4,    # DEFAULT 4
            'OTP_SMS_TEMPLATE_ID'   : 1,    
        }
    },
    'SMS': {
        'SMS_SERVICE': 'PARSIAN_WEBCO_IR',  # PARSIAN_WEBCO_IR , MELI_PAYAMAK_COM , KAVENEGAR_COM
        'SETTINGS': {
            'PARSIAN_WEBCO_IR_API_KEY'  : '',
            'MELI_PAYAMAK_COM_USERNAME' : '',
            'MELI_PAYAMAK_COM_PASSWORD' : '',
            'MELI_PAYAMAK_COM_FROM'     : '',
            'KAVENEGAR_COM_API_KEY'     : '656F6635756C485658666F6A52307562456C4F5043714769597A58434D2B527974434534672B50445736553D',
            'KAVENEGAR_COM_FROM'        : '2000660110',
        },
        'TEMPLATES': {
            'T1': 1,
            'T2': 2,
            'T3': 3,
            'T4': 4,
            'T5': 5,
            'T6': 6,
            'T7': 7,
            'T8': 8,
            'T9': 9,
        }
    }
}
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SERVICE_NAME = 'DJANGO_CHELSERU'

AUTH_METHOD = [(0, 'OTP'), (1, 'PASSWD')]
AUTH_SERVICES = [(0, 'rest_framework_simplejwt')]
SMS_SERVICES = [(0, 'PARSIAN_WEBCO_IR'),(1, 'MELI_PAYAMAK_COM') ,(2, 'KAVENEGAR_COM')]

def auth_init_check():
    try:
        auth_mode = 'OTP'
        auth_service = 'rest_framework_simplejwt'
        options = {
            'len': 8,
            'exp_time': 4,
            #'default_sms_template': 1
        }
        if not hasattr(settings, SERVICE_NAME):
            raise ImproperlyConfigured(f'{SERVICE_NAME} must be defined in settings.py.')
        
        else:
            _auth = getattr(settings, SERVICE_NAME).get('AUTH')
            if _auth:
                _auth_mode = _auth.get('AUTH_MODE')
                _auth_service = _auth.get('AUTH_SERVICE')
                _opt_len = _auth.get('OPTIONS').get('OTP_LENGTH', 6)
                _opt_exp_time = _auth.get('OPTIONS').get('OTP_EXPIRE_PER_MINUTES', 4)
                _otp_sms_template = _auth.get('OPTIONS').get('OTP_SMS_TEMPLATE_ID', 0)

                if _auth_mode:
                    if _auth_mode in list(map(lambda x: x[1], AUTH_METHOD)):
                        auth_mode = _auth_mode

                    else:
                        raise ImproperlyConfigured(f'AUTH_METHOD must be choice between {list(map(lambda x: x[1], AUTH_METHOD))}.')

                if _auth_service:
                    if _auth_service not in list(map(lambda x: x[1], AUTH_SERVICES)):
                        raise ImproperlyConfigured(f'AUTH_SERVICES must be choice between {list(map(lambda x: x[1], AUTH_SERVICES))}.')
                    else:
                        auth_service = _auth_service
                
                if _opt_len and isinstance(_opt_len, int):
                    if _opt_len < 3 or _opt_len > 10:
                        raise ImproperlyConfigured("OTP_LENGTH must be less than or equal to 10 and greater than or equal to 3.")
                
                if _opt_exp_time and isinstance(_opt_exp_time, int):
                    if _opt_exp_time <= 0:
                        raise ImproperlyConfigured("OTP_EXPIRE_PER_MINUTES must be greater than 0.")

                # if _otp_sms_template and isinstance(_otp_sms_template, int):
                #     if _otp_sms_template <= 0:
                #         raise ImproperlyConfigured("SMS_TEMPLATE_ID must be greater than 0.")

                options['exp_time'] = _opt_exp_time
                options['len'] = _opt_len
                options['default_sms_template'] = _otp_sms_template

        return {'AUTH_METHOD': auth_mode, 'AUTH_SERVICE': auth_service, 'OPTIONS': options}
    except ImproperlyConfigured as e:
        print(f"Configuration Error: {e}")
        raise
    except:
        pass
    return False


def sms_init_check():
    try:
        sms_service = None
        options = {}
        templates = {}
        if not hasattr(settings, SERVICE_NAME):
            raise ImproperlyConfigured(f'{SERVICE_NAME} must be defined in settings.py.')
        
        else:
            if not getattr(settings, SERVICE_NAME).get('SMS'):
                raise ImproperlyConfigured(f'SMS key must be defined in {SERVICE_NAME}')
            
            else:
                templates = getattr(settings, SERVICE_NAME).get('SMS').get('TEMPLATES', {})
                sms_service = getattr(settings, SERVICE_NAME).get('SMS').get('SMS_SERVICE')
                if not sms_service:
                    raise ImproperlyConfigured(f'SMS_SERVICE key must be defined in {SERVICE_NAME}: SMS .')
                
                else:
                    if sms_service not in list(map(lambda x: x[1], SMS_SERVICES)):
                        raise ImproperlyConfigured(f'SMS_SERVICE must be choice between {list(map(lambda x: x[1], SMS_SERVICES))}.')
                    
                    else:
                        if not getattr(settings, SERVICE_NAME).get('SMS').get('SETTINGS'):
                            raise ImproperlyConfigured(f'SETTINGS key must be defined in {SERVICE_NAME}: SMS .')
                        
                        else:
                            if sms_service == 'PARSIAN_WEBCO_IR':
                                api_key = getattr(settings, SERVICE_NAME).get('SMS').get('SETTINGS').get('PARSIAN_WEBCO_IR_API_KEY')
                                if not api_key:
                                    raise ImproperlyConfigured(f'PARSIAN_WEBCO_IR_API_KEY must be defined in {SERVICE_NAME}: SMS: SETTINGS, To access the SMS service API, you need to have API keys.')
                                
                                else:
                                    options['api_key'] = api_key
                            
                            # -------------------------------------
                            elif sms_service == 'MELI_PAYAMAK_COM':
                                username = getattr(settings, SERVICE_NAME).get('SMS').get('SETTINGS').get('MELI_PAYAMAK_COM_USERNAME')
                                if not username:
                                    raise ImproperlyConfigured(f'MELI_PAYAMAK_COM_USERNAME must be defined in {SERVICE_NAME}: SMS: SETTINGS, To access the SMS service API, you need to have API keys.')
                                
                                else:
                                    options['username'] = username

                                password = getattr(settings, SERVICE_NAME).get('SMS').get('SETTINGS').get('MELI_PAYAMAK_COM_PASSWORD')
                                if not password:
                                    raise ImproperlyConfigured(f'MELI_PAYAMAK_COM_PASSWORD must be defined in {SERVICE_NAME}: SMS: SETTINGS, To access the SMS service API, you need to have API keys.')
                                
                                else:
                                    options['password'] = password

                                _from = getattr(settings, SERVICE_NAME).get('SMS').get('SETTINGS').get('MELI_PAYAMAK_COM_FROM')
                                if not _from:
                                    raise ImproperlyConfigured(f'MELI_PAYAMAK_COM_FROM must be defined in {SERVICE_NAME}: SMS: SETTINGS, To send an SMS, the sender`s number is required.')
                                
                                else:
                                    options['from'] = _from
                            
                            # -------------------------------------
                            elif sms_service == 'KAVENEGAR_COM':
                                api_key = getattr(settings, SERVICE_NAME).get('SMS').get('SETTINGS').get('KAVENEGAR_COM_API_KEY')
                                if not api_key:
                                    raise ImproperlyConfigured(f'KAVENEGAR_COM_API_KEY must be defined in {SERVICE_NAME}: SMS: SETTINGS, To access the SMS service API, you need to have API keys.')
                                
                                else:
                                    options['api_key'] = api_key

                                _from = getattr(settings, SERVICE_NAME).get('SMS').get('SETTINGS').get('KAVENEGAR_COM_FROM')
                                if not _from:
                                    raise ImproperlyConfigured(f'KAVENEGAR_COM_FROM must be defined in {SERVICE_NAME}: SMS: SETTINGS, To send an SMS, the sender`s number is required.')
                                
                                else:
                                    options['from'] = _from

        return {'SMS_SERVICE': sms_service, 'SETTINGS': options, 'TEMPLATES': templates}
    except ImproperlyConfigured as e:
        print(f"Configuration Error: {e}")
        raise
    except:
        pass
    return False


