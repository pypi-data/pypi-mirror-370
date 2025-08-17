from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_409_CONFLICT, HTTP_502_BAD_GATEWAY, HTTP_401_UNAUTHORIZED
from .models import User
from .serializers import OTPCodeSerializer
from .validators import mobile_number as mobile_validator
from .services import ParsianWebcoIr, MeliPayamakCom, KavenegarCom
from .settings import otp_code_expire, init_check, sms_service_check


class OTPCodeSend(APIView):
    permission_classes = (AllowAny, )
    serializer_class = OTPCodeSerializer
    model = serializer_class.Meta.model

    def post(self, request):
        """
        prams:
            mobile_number:   str (len: 11)   (exp: 09211892425)

        response:
            HTTP_409_CONFLICT               {'error': 'Try again after - minutes..'}
            HTTP_204_NO_CONTENT             {'error': [params requirements and validations]}
            HTTP_500_INTERNAL_SERVER_ERROR  {'error': 'contact the support..'}
            HTTP_200_OK                     {'details': 'The OTP code was sent correctly.'}
            HTTP_502_BAD_GATEWAY            {'details': 'The SMS service provider was unable to process the request.'}
            HTTP_401_UNAUTHORIZED           {'details': 'Authentication is not accepted, check your token and if the token has not been received, obtain it from your SMS service provider.'}
        """
        try:
            assert 'mobile_number' in request.data, 'mobile_number is required.'
            mobile_number = request.data['mobile_number']
            assert mobile_number, 'mobile_number may not be blank.'
            mobile_number_isvalid = mobile_validator(mobile_number)
            assert mobile_number_isvalid == True, mobile_number_isvalid
            
            icheck = init_check()
            if icheck and isinstance(icheck, dict) and 'SMS_BACKEND' in icheck:
                sms_service = icheck['SMS_BACKEND']
                if sms_service_check(sms_service):
                    otp_code = self.model(mobile=mobile_number)
                    obj = otp_code.save()
                    if isinstance(obj, self.model):
                        # send sms:                    
                        match sms_service:
                            case 'PARSIAN_WEBCO_IR':
                                service = ParsianWebcoIr(mobile=obj.mobile)
                                response = service.send_otp_code(code=obj.code)
                                if isinstance(response, dict) and 'status' in response:
                                    if response['status'] == 200:
                                        return Response({'details': 'The OTP code was sent correctly.'}, status=HTTP_200_OK)
                                    elif response['status'] == 100:
                                        return Response({'details': 'The SMS service provider was unable to process the request.'}, status=HTTP_502_BAD_GATEWAY)
                                    elif response['status'] == 401:
                                        return Response({'details': 'Authentication is not accepted, check your token and if the token has not been received, obtain it from your SMS service provider.'}, status=HTTP_401_UNAUTHORIZED)
                    
                            case 'MELI_PAYAMAK_COM':
                                service = MeliPayamakCom(mobile=obj.mobile)
                                response = service.send_message(message=obj.code)
                                if response in [0, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 17, 35]:
                                    return Response({'details': 'The SMS service provider was unable to process the request.', 'errorCode': response}, status=HTTP_502_BAD_GATEWAY)
                                else:
                                    return Response({'details': 'The OTP code was sent correctly.', 'smsID': response}, status=HTTP_200_OK)

                            case 'KAVENEGAR_COM':
                                service = KavenegarCom(mobile=mobile_number)
                                response = service.send_message(message=obj.code)
                                try:
                                    response_json = response.json()
                                    entries = response_json.get('entries', [])
                                    _return = response_json.get('return', [])
                                    if entries:
                                        response_data = entries[0]
                                        if response.status_code == 200 and response_data.get('status') in [5, 10]:
                                            return Response({'details': 'The OTP code was sent correctly.', 'messageid': response_data.get('messageid', '')}, status=HTTP_200_OK)
                                        else:
                                            return Response({'details': 'The SMS service provider was unable to process the request.', 'errorcode': response_data.get('status', ''), 'errortext': response_data.get('statustext', ''), 'message': response_data.get('message', '')}, HTTP_502_BAD_GATEWAY)
                                    elif  _return:
                                        return Response({'details': 'The SMS service provider was unable to process the request.', 'message': _return.get('message', '')}, status=HTTP_502_BAD_GATEWAY)
                                except (ValueError, KeyError, IndexError) as e:
                                    return Response({'details': 'Invalid response structure.', 'error': str(e)}, status=HTTP_502_BAD_GATEWAY)


                    else:
                        if obj == 409:
                            return Response({'error': f'Try again after {otp_code_expire()} minutes.'}, status=HTTP_409_CONFLICT)
        except AssertionError as e:
            return Response({'error': str(e)}, status=HTTP_204_NO_CONTENT)
        except:
            pass
        return Response({'error': 'An error occurred while generating or sending the otpcode, please contact the www.chelseru.com support team.'}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class Authentication(APIView):
    permission_classes = (AllowAny, )
    serializer_class = OTPCodeSerializer
    model = serializer_class.Meta.model

    def post(self, request):
        """
        prams:
            mobile_number:   str (len: 11)     (exp: 09211892425)
            code: str (len: otp_code_length()) (exp: 652479)
            pre_username: str (len: 7)         (exp: service)

        response:
            HTTP_204_NO_CONTENT             {'error': [params requirements and validations]}
            HTTP_500_INTERNAL_SERVER_ERROR  {'error': 'contact the support..'}
            HTTP_200_OK                     {'access': '', 'refresh': ''}
        """
        try:
            assert 'mobile_number' in request.data, 'mobile_number is required.'
            mobile_number = request.data['mobile_number']
            assert mobile_number, 'mobile_number may not be blank.'
            mobile_number_isvalid = mobile_validator(mobile_number)
            assert mobile_number_isvalid == True, mobile_number_isvalid
            assert 'code' in request.data, 'code is required.'
            
            icheck = init_check()
            if icheck and isinstance(icheck, dict) and 'AUTHENTICATION' in icheck:
                otp_code = request.data['code']
                otp = self.model.objects.filter(mobile=mobile_number).filter(code=otp_code).first()
                if otp:
                    if otp.check_code():
                        # login / signup
                        group = int(request.data['group']) if 'group' in request.data else 0
                        user, created = User.objects.get_or_create(mobile=mobile_number, group=group)
                        if user:
                            auth_service = icheck['AUTHENTICATION']
                            match auth_service:
                                case 'rest_framework_simplejwt':
                                    from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, BlacklistedToken
                                    access_token = AccessToken.for_user(user=user.user)
                                    refresh_token = RefreshToken.for_user(user=user.user)
                                    return Response({'access': str(access_token), 'refresh': str(refresh_token)}, status=HTTP_200_OK)
                        
                else:
                    return Response({'error': 'The code sent to this mobile number was not found.'}, status=HTTP_401_UNAUTHORIZED)
        except AssertionError as e:
            return Response({'error': str(e)}, status=HTTP_204_NO_CONTENT)
        except:
            pass
        return Response({'error': 'An error occurred while generating or sending the otpcode, please contact the www.chelseru.com support team.'}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class MessageSend(APIView):
    permission_classes = (AllowAny, )
    #serializer_class = MessageSerializer
    #model = serializer_class.Meta.model

    def post(self, request):
        """
        prams:
            mobile_number:   str (len: 11)   (exp: 09211892425)
            message_text:    str (len: 290)

        response:
            HTTP_204_NO_CONTENT             {'error': [params requirements and validations]}
            HTTP_500_INTERNAL_SERVER_ERROR  {'error': 'contact the support..'}
            HTTP_200_OK                     {'details': 'The Message was sent correctly.'}
            HTTP_502_BAD_GATEWAY            {'details': 'The SMS service provider was unable to process the request.'}
            HTTP_401_UNAUTHORIZED           {'details': 'Authentication is not accepted, check your token and if the token has not been received, obtain it from your SMS service provider.'}
        """
        try:
            assert 'mobile_number' in request.data, 'mobile_number is required.'
            mobile_number = request.data['mobile_number']
            assert mobile_number, 'mobile_number may not be blank.'
            mobile_number_isvalid = mobile_validator(mobile_number)
            assert mobile_number_isvalid == True, mobile_number_isvalid
            
            assert 'message_text' in request.data, 'message_text is required.'
            message_text = request.data['message_text']

            icheck = init_check()
            if icheck and isinstance(icheck, dict) and 'SMS_BACKEND' in icheck:
                sms_service = icheck['SMS_BACKEND']
                if sms_service_check(sms_service):
                    # send sms:
                    match sms_service:
                        case 'PARSIAN_WEBCO_IR':
                            assert 'template_id' in request.data, 'template_id is required, in the PARSIAN_WEBCO_IR.'
                            template_id = request.data['template_id']
                            service = ParsianWebcoIr(mobile=mobile_number)
                            response = service.send_message(message=message_text, template_id=template_id)
                            if isinstance(response, dict) and 'status' in response:
                                if response['status'] == 200:
                                    return Response({'receiver': mobile_number, 'message': message_text}, status=HTTP_200_OK)
                                elif response['status'] == 100:
                                    return Response({'details': 'The SMS service provider was unable to process the request.'}, status=HTTP_502_BAD_GATEWAY)
                                elif response['status'] == 401:
                                    return Response({'details': 'Authentication is not accepted, check your token and if the token has not been received, obtain it from your SMS service provider.'}, status=HTTP_401_UNAUTHORIZED)
                        case 'MELI_PAYAMAK_COM':
                                service = MeliPayamakCom(mobile=mobile_number)
                                response = service.send_message(message=message_text)
                                if response in [0, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 17, 35]:
                                    return Response({'details': 'The SMS service provider was unable to process the request.', 'errorcode': response}, status=HTTP_502_BAD_GATEWAY)
                                else:
                                    return Response({'receiver': mobile_number, 'message': message_text, 'messageid': response}, status=HTTP_200_OK)
                        case 'KAVENEGAR_COM':
                            service = KavenegarCom(mobile=mobile_number)
                            response = service.send_message(message=message_text)
                            try:
                                response_json = response.json()
                                entries = response_json.get('entries', [])
                                _return = response_json.get('return', [])
                                if entries:
                                    response_data = entries[0]
                                    if response.status_code == 200 and response_data.get('status') in [5, 10]:
                                        return Response({'receiver': response_data.get('receptor', ''), 'message': response_data.get('message', ''), 'messageid': response_data.get('messageid', '')}, status=HTTP_200_OK)
                                    else:
                                        return Response({'details': 'The SMS service provider was unable to process the request.', 'errorcode': response_data.get('status', ''), 'errortext': response_data.get('statustext', ''), 'message': response_data.get('message', '')}, HTTP_502_BAD_GATEWAY)
                                elif  _return:
                                    return Response({'details': 'The SMS service provider was unable to process the request.', 'message': _return.get('message', '')}, status=HTTP_502_BAD_GATEWAY)
                            except (ValueError, KeyError, IndexError) as e:
                                return Response({'details': 'Invalid response structure.', 'error': str(e)}, status=HTTP_502_BAD_GATEWAY)

        except AssertionError as e:
            return Response({'error': str(e)}, status=HTTP_204_NO_CONTENT)
        except:
            pass
        return Response({'error': 'An error occurred while generating or sending the otpcode, please contact the www.chelseru.com support team.'}, status=HTTP_500_INTERNAL_SERVER_ERROR)
