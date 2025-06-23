from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from .models import User
from transaction.models import Transaction, Plan


@receiver(pre_save, sender=User)
def save_name(sender, instance, *args, **kwargs):

    name, domain = instance.email.split('@')
    
    if not instance.name:
        instance.name = name.replace('.', ' ').strip().capitalize()[:25] #eg: paul@email.com -> Paul


@receiver(post_save, sender=User)
def update_workflow_status(sender, instance, created, **kwargs):
    
    # for now lets attribut a plan freely to all users
    has_phone = bool(instance.phone_number)
    has_activity = bool(instance.activity_area)
    has_plan = Transaction.objects.filter(user=instance, plan__isnull=False).exists()
    telegram_token = bool(instance.telegram_token)
    # Si pas de plan, on crée une transaction avec le plan gratuit (ex: Plan gratuit id=1)
    if not has_plan:
        try:
            free_plan = Plan.objects.get(name="Starters")  # ou utiliser un autre critère pour le plan gratuit
        except Plan.DoesNotExist:
            free_plan = None

        if free_plan:
            Transaction.objects.create(user=instance, plan=free_plan, subscription_status=1)  # status active
            has_plan = True  # on met à jour la variable pour la suite

    if has_phone and has_activity and has_plan and telegram_token:
        new_status = 'active'
    elif not has_phone or not has_activity:
        new_status = 'info_needed'
    elif not telegram_token:
        new_status = 'pending'
    else:
        new_status = 'awaiting_payment'

    if instance.workflow_status != new_status:
        # On évite la boucle infinie en passant par update
        User.objects.filter(pk=instance.pk).update(workflow_status=new_status)

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