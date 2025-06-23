from django.dispatch import receiver
from django.db.models.signals import pre_save

from .models import User
from transaction.models import Transaction


@receiver(pre_save, sender=User)
def save_name(sender, instance, *args, **kwargs):

    name, domain = instance.email.split('@')
    
    if not instance.name:
        instance.name = name.replace('.', ' ').strip().capitalize()[:25] #eg: paul@email.com -> Paul

    has_phone = bool(instance.phone_number)
    has_activity = bool(instance.activity_area)
    has_plan = Transaction.objects.filter(user=instance, plan__isnull=False).exists()

    if has_phone and has_activity and has_plan:
        instance.workflow_status = 'active'
    else:
        if not has_phone or not has_activity:
            instance.workflow_status = 'info_needed'
        elif not has_plan:
            instance.workflow_status = 'awaiting_payment'

from allauth.socialaccount.models import SocialToken
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

@receiver(post_save, sender=SocialToken)
def save_user_tokens(sender, instance, created, **kwargs):
    account = instance.account
    if account.provider == 'google':
        user = account.user
        user.access_token = instance.token
        user.refresh_token = instance.token_secret or ''
        user.token_expiry = instance.expires_at
        print("Token saved for user:", user.email)
        user.save()