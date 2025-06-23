from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialToken

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        
        if sociallogin.account.provider == 'google':
            print("Saving Google tokens from sociallogin.token for user:", user.email)
            token = sociallogin.token  # plus fiable ici que SocialToken.objects.filter(...)
            if token:
                user.access_token = token.token
                user.refresh_token = getattr(token, 'token_secret', None)
                user.token_expiry = token.expires_at
                user.save()

        return user