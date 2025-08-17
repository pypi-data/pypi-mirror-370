from django.contrib import admin
from .models import User, OTPCode

@admin.register(User)
class MobileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user__id', 'user__username', 'mobile', 'user__is_active']


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'mobile', 'created_at']
    ordering = ('-created_at', )

