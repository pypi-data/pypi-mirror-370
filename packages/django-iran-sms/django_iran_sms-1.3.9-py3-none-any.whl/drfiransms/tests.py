import json
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from .models import OTPCode
from .models import OTPCode, User as CustomUser


class TestParsianWebcoIrService(APITestCase):
    user = get_user_model()

    @patch('drfiransms.views.ParsianWebcoIr.send_otp_code')
    @patch('drfiransms.views.sms_service_check', return_value=True)
    @patch('drfiransms.views.init_check', return_value={'SMS_BACKEND': 'PARSIAN_WEBCO_IR'})
    def test_send_otp_code_success(self, mock_init, mock_check, mock_send):
        mock_send.return_value = {'status': 200}
        client = APIClient()
        response = client.post('/drf/send/otpcode/', {'mobile_number': '09167332792'})
        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once()
    

    @patch('drfiransms.views.ParsianWebcoIr.send_message')
    @patch('drfiransms.views.sms_service_check', return_value=True)
    @patch('drfiransms.views.init_check', return_value={'SMS_BACKEND': 'PARSIAN_WEBCO_IR'})
    def test_send_message_success(self, mock_init, mock_check, mock_send):
        mock_send.return_value = {'status': 200}
        client = APIClient()
        response = client.post('/drf/send/message/', {'mobile_number': '09167332792', 'message_text': 'hello louristan.', 'template_id': '1'})
        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once()

    
    def test_authentication_success(self):
        mobile_number = '09167332792'
        otp = OTPCode.objects.create(
            mobile= mobile_number,
        )
        otp_code = OTPCode.objects.filter(mobile= mobile_number).first().code
        client = APIClient()
        response = client.post('/drf/auth/', {'mobile_number': mobile_number, 'code': otp_code, 'group': '1'})

        self.assertEqual(response.status_code, 200)


class TestMelipayamakComService(APITestCase):

    @patch('drfiransms.views.MeliPayamakCom.send_message', return_value='123456')
    @patch('drfiransms.views.sms_service_check', return_value=True)
    @patch('drfiransms.views.init_check', return_value={'SMS_BACKEND': 'MELI_PAYAMAK_COM'})
    def test_send_otp_code_success(self, mock_init, mock_check, mock_send):
        client = APIClient()
        response = client.post('/drf/send/otpcode/', {'mobile_number': '09167332792'})
        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once()

    
    @patch('drfiransms.views.MeliPayamakCom.send_message', return_value='123456')
    @patch('drfiransms.views.sms_service_check', return_value=True)
    @patch('drfiransms.views.init_check', return_value={'SMS_BACKEND': 'MELI_PAYAMAK_COM'})
    def test_send_message_success(self, mock_init, mock_check, mock_send):
        client = APIClient()
        response = client.post('/drf/send/message/', {'mobile_number': '09167332792', 'message_text': 'hello louristan'})
        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once()

    
    def test_authentication_success(self):
        mobile_number = '09167332792'

        otp = OTPCode.objects.create(
            mobile= mobile_number
        )

        otp_code = OTPCode.objects.filter(mobile=mobile_number).first().code

        client = APIClient()
        response = client.post('/drf/auth/', {'mobile_number': mobile_number, 'code': otp_code, 'group': '0'})
        print(response)
        self.assertEqual(response.status_code, 200)

