from django.db import models
from django.contrib.auth.models import User as default_user
from django.utils.timezone import now, timedelta
from random import randint
from .settings import otp_code_length, otp_code_expire


class User(models.Model):
    user = models.OneToOneField(default_user, on_delete=models.CASCADE, related_name='mobile')
    mobile = models.CharField(max_length=11)
    group = models.IntegerField(default=0, help_text='choice group type or user level, with numbers.')

    def __str__(self):
        return f'{self.user.username} | {self.mobile}'


class OTPCode(models.Model):
    code = models.CharField(max_length=10)
    mobile = models.CharField(max_length=11)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.code} -> {self.mobile} | {self.created_at}'

    def save(self, *args, **kwargs):
        try:
            objs = OTPCode.objects.filter(mobile=self.mobile)
            if objs:
                if now().timestamp() > (objs.first().created_at + timedelta(seconds=otp_code_expire() * 60)).timestamp():
                    objs.delete()
                else:
                    return 409

            code = str(randint(int('1' + (otp_code_length() - 1) * '0'), int(otp_code_length() * '9')))
            self.code = code
            super().save(*args, **kwargs)
            return self
        except:
            pass
        return 500

    def check_code(self):
        try:
            if now().timestamp() <= (self.created_at + timedelta(seconds=otp_code_expire() * 60)).timestamp():
                self.delete()
                return True
            self.delete()
        except:
            pass
        return False

