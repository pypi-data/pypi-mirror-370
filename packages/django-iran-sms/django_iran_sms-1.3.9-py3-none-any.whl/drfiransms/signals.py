from django.contrib.auth.models import User as DefaultUser
from .models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         mobile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.mobile.save()

@receiver(pre_save, sender=User)
def create_user_if_not_exists(sender, instance, **kwargs):
    if not instance.user_id:
        default_user, created = DefaultUser.objects.get_or_create(mobile__mobile=instance.mobile, mobile__group=instance.group, 
                                                                  defaults={'username': f'G{instance.group}-{instance.mobile}'})
        if created:
            instance.user = default_user