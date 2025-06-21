from django.dispatch import receiver
from django.db.models.signals import pre_save

from .models import User


@receiver(pre_save, sender=User)
def save_name(sender, instance, *args, **kwargs):

    name, domain = instance.email.split('@')
    
    if not instance.name:
        instance.name = name.replace('.', ' ').strip().capitalize()[:25] #eg: paul@email.com -> Paul


from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.dispatch import receiver
from datetime import datetime
import pytz

@receiver([social_account_added, social_account_updated])
def get_google_tokens(request, sociallogin, **kwargs):
    print("Signal triggered for social account added or updated.\n\n\n")
    if sociallogin.account.provider == 'google':
        token = SocialToken.objects.filter(account=sociallogin.account).first()
        if token:
            user = sociallogin.user
            user.access_token = token.token
            print(f"Access token: {user.access_token}")
            user.refresh_token = token.token_secret  # Vérifie si présent
            print(f"Refresh token: {user.refresh_token}")
            if token.expires_at:
                user.token_expiry = token.expires_at  # déjà un datetime avec timezone
                print(f"Token expires at: {user.token_expiry}")
            user.save()