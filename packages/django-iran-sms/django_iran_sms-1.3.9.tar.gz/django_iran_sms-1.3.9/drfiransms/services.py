import requests, json
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from zeep import Client


class ParsianWebcoIr:
    """
        token
        TemplateID
        MessageVars
        Receiver
        delay
    """
    TOKEN = None
    HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
    def __init__(self, mobile, *args, **kwargs):
        try:
            # Give TOKEN from DJANGO_IRAN_SMS { PARSIAN_WEBCO_IR { TOKEN } }
            if not hasattr(settings, 'DJANGO_IRAN_SMS'):
                raise ImproperlyConfigured('DJANGO_IRAN_SMS must be defined in settings.py .')

            if 'PARSIAN_WEBCO_IR' not in settings.DJANGO_IRAN_SMS:
                raise ImproperlyConfigured('PARSIAN_WEBCO_IR must be defined in settings.py -> DJANGO_IRAN_SMS.')

            if 'API_KEY' not in settings.DJANGO_IRAN_SMS['PARSIAN_WEBCO_IR']:
                raise ImproperlyConfigured('API_KEY must be defined in settings.py -> DJANGO_IRAN_SMS:PARSIAN_WEBCO_IR.')
        except ImproperlyConfigured as e:
            print(f"Configuration Error: {e}")
            raise
        else:
            self.TOKEN = settings.DJANGO_IRAN_SMS['PARSIAN_WEBCO_IR']['API_KEY']
        self.RECEIVER = mobile

    def send_otp_code(self, code, template_id=None):
        try:
            if not template_id:
                if not hasattr(settings, 'DJANGO_IRAN_SMS'):
                    raise ImproperlyConfigured('DJANGO_IRAN_SMS must be defined in settings.py .')

                if 'PARSIAN_WEBCO_IR' not in settings.DJANGO_IRAN_SMS:
                    raise ImproperlyConfigured('PARSIAN_WEBCO_IR must be defined in settings.py -> DJANGO_IRAN_SMS.')

                if 'TEMPLATES' not in settings.DJANGO_IRAN_SMS['PARSIAN_WEBCO_IR']:
                    raise ImproperlyConfigured('TEMPLATES must be defined in settings.py -> DJANGO_IRAN_SMS:PARSIAN_WEBCO_IR.')

                if 'OTP_CODE' not in settings.DJANGO_IRAN_SMS['PARSIAN_WEBCO_IR']['TEMPLATES']:
                    raise ImproperlyConfigured('OTP_CODE must be defined in settings.py -> DJANGO_IRAN_SMS:PARSIAN_WEBCO_IR:TEMPLATES.')

                template_id = settings.DJANGO_IRAN_SMS['PARSIAN_WEBCO_IR']['TEMPLATES']['OTP_CODE']

            api_url = 'https://api.parsianwebco.ir/webservice-send-sms/send'
            data = {
                'token': self.TOKEN,
                'TemplateID': template_id,
                'MessageVars': code,
                'Receiver': self.RECEIVER,
                'delay': 1
            }
            return json.loads(requests.post(url=api_url, data=data, headers=self.HEADERS).content)
            """
                response:
                    status:
                        200 ok
                        100 faild
                        401 no authenticated
            """
        except ImproperlyConfigured as e:
            print(f"Configuration Error: {e}")
            raise
        return False

    def send_message(self, message, template_id):
        try:
            api_url = 'https://api.parsianwebco.ir/webservice-send-sms/send'
            data = {
                'token': self.TOKEN,
                'TemplateID': template_id,
                'MessageVars': message,
                'Receiver': self.RECEIVER,
                'delay': 1
            }
            return json.loads(requests.post(url=api_url, data=data, headers=self.HEADERS).content)
            """
                response:
                    status:
                        200 ok
                        100 faild
                        401 no authenticated
            """
        except:
            return False


class MeliPayamakCom:
    '''
    username
    password
    from
    to
    text
    '''
    USERNAME = None
    PASSWORD = None
    FROM = None

    def __init__(self, mobile, *args, **kwargs):
        try:
            # Give TOKEN from DJANGO_IRAN_SMS { PARSIAN_WEBCO_IR { TOKEN } }
            if not hasattr(settings, 'DJANGO_IRAN_SMS'):
                raise ImproperlyConfigured('DJANGO_IRAN_SMS must be defined in settings.py .')

            if 'MELI_PAYAMAK_COM' not in settings.DJANGO_IRAN_SMS:
                raise ImproperlyConfigured('MELI_PAYAMAK_COM must be defined in settings.py -> DJANGO_IRAN_SMS.')

            if 'USERNAME' not in settings.DJANGO_IRAN_SMS['MELI_PAYAMAK_COM']:
                raise ImproperlyConfigured('USERNAME must be defined in settings.py -> DJANGO_IRAN_SMS:MELI_PAYAMAK_COM.')

            if 'PASSWORD' not in settings.DJANGO_IRAN_SMS['MELI_PAYAMAK_COM']:
                raise ImproperlyConfigured('PASSWORD must be defined in settings.py -> DJANGO_IRAN_SMS:MELI_PAYAMAK_COM.')
            
            if 'FROM' not in settings.DJANGO_IRAN_SMS['MELI_PAYAMAK_COM']:
                raise ImproperlyConfigured('FROM must be defined in settings.py -> DJANGO_IRAN_SMS:MELI_PAYAMAK_COM.')
        
        except ImproperlyConfigured as e:
            print(f"Configuration Error: {e}")
            raise
        else:
            self.USERNAME = settings.DJANGO_IRAN_SMS['MELI_PAYAMAK_COM']['USERNAME']
            self.PASSWORD = settings.DJANGO_IRAN_SMS['MELI_PAYAMAK_COM']['PASSWORD']
            self.FROM = settings.DJANGO_IRAN_SMS['MELI_PAYAMAK_COM']['FROM']
        self.RECEIVER = mobile

    def send_message(self, message):
        try:
            client = Client(wsdl='https://api.payamak-panel.com/post/Send.asmx?wsdl')
            data = {
                'username': self.USERNAME,
                'password': self.PASSWORD,
                'from': self.FROM,
                'to': self.RECEIVER,
                'text': message,
                'isflash': False
            }

            response = client.service.SendSimpleSMS2(**data)
            return response
            """
                response:
                    status:
                        recld (Unique value for each successful submission)
                        0   The username or password is incorrect.
                        2   Not enough credit.
                        3   Limit on daily sending.
                        4   Limit on sending volume.
                        5   The sender's number is not valid.
                        6   The system is being updated.
                        7   The text contains the filtered word.
                        9   Sending from public lines via web service is not possible.
                        10  The desired user is not active.
                        11  Not sent.
                        12  The user's credentials are not complete.
                        14  The text contains a link.
                        15  Sending to more than 1 mobile number is not possible without inserting "لغو11".
                        16  No recipient number found
                        17  The text of the SMS is empty.
                        35  In REST, it means that the number is on the blacklist of communications.
            """
        except:
            return False


class KavenegarCom:
    '''
    API_KEY
    receptor
    message
    sender
    '''
    API_KEY = None
    SENDER = None
    
    def __init__(self, mobile, *args, **kwargs):
        try:
            # Give TOKEN from DJANGO_IRAN_SMS { PARSIAN_WEBCO_IR { TOKEN } }
            if not hasattr(settings, 'DJANGO_IRAN_SMS'):
                raise ImproperlyConfigured('DJANGO_IRAN_SMS must be defined in settings.py .')

            if 'KAVENEGAR_COM' not in settings.DJANGO_IRAN_SMS:
                raise ImproperlyConfigured('KAVENEGAR_COM must be defined in settings.py -> DJANGO_IRAN_SMS.')

            if 'API_KEY' not in settings.DJANGO_IRAN_SMS['KAVENEGAR_COM']:
                raise ImproperlyConfigured('API_KEY must be defined in settings.py -> DJANGO_IRAN_SMS:KAVENEGAR_COM.')

            if 'FROM' not in settings.DJANGO_IRAN_SMS['KAVENEGAR_COM']:
                raise ImproperlyConfigured('FROM must be defined in settings.py -> DJANGO_IRAN_SMS:KAVENEGAR_COM.')

        except ImproperlyConfigured as e:
            print(f"Configuration Error: {e}")
            raise
        else:
            self.API_KEY = settings.DJANGO_IRAN_SMS['KAVENEGAR_COM']['API_KEY']
            self.SENDER = settings.DJANGO_IRAN_SMS['KAVENEGAR_COM']['FROM']
        self.RECEIVER = mobile


    def send_message(self, message):
        try:
            api_url = f'https://api.kavenegar.com/v1/{self.API_KEY}/sms/send.json'
            data = {
                'sender': self.SENDER,
                'receptor': self.RECEIVER,
                'message': message,
            }
            response = requests.post(url=api_url, data=data)
            return response
            """
                response:
                    messageid Unique identifier of this SMS (To know the status of the sent SMS, this value is the input to the Status method.)
                    status:
                        200   if status is 10 & 5 , message received.
                        400   The parameters are incomplete.
                        401   Account has been deactivated.
                        403   The API-Key identification code is not valid.
                        406   Empty mandatory parameters sent.
                        411   The recipient is invalid.
                        412   The sender is invalid.
                        413   The message is empty or the message length exceeds the allowed limit. The maximum length of the entire SMS text is 900 characters.
                        414   The request volume exceeds the allowed limit, sending SMS: maximum 200 records per call and status control: maximum 500 records per call
                        416   The originating service IP does not match the settings.
                        418   Your credit is not sufficient.
                        451   Excessive calls within a specific time period are restricted to IP addresses.
            """
        except:
            return False
