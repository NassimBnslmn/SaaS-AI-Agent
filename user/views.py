import jwt
import json

from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.utils.encoding import force_str
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import User
from .forms import CustomUserCreationForm, UserProfileForm
from utils.token_generator import send_token

@login_required
def dashboard_view(request):
    """
        Render the dashboard view for authenticated users.
    """
    if request.user.is_superuser:
        return redirect(reverse('admin:index'))
    return render(request, 'html/users/dashboard.html', context={
        'user': request.user
    })

from transaction.models import Transaction, SUBSCRIPTION_STATUS, Plan

@login_required
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return render(request, 'html/users/profile.html', {'form': form})
        else:
            messages.error(request, 'Erreur lors de la mise à jour du profil.')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'html/users/profile.html', {'form': form})


@login_required
def subscription_view(request):
    plans = Plan.objects.all()
    # Récupérer la transaction active de l'utilisateur (ou None)
    active_plan = (
        Transaction.objects.filter(user=request.user, subscription_status=SUBSCRIPTION_STATUS.ACTIVE)
        .select_related('plan')
        .first()
    )
    context = {
        'plans': plans,
        'active_plan': active_plan.plan if active_plan else None,
    }
    return render(request, 'html/users/plan.html', context)



def login_view(request):
    next_url = request.GET.get('next', '')

    if request.user.is_authenticated:
        if next_url and next_url != request.path:
            return redirect(next_url)
        
        return redirect('home')

    if request.method == "GET":
        return render(request, 'html/authentication/login.html', {
            'next': next_url
        })

    email = request.POST["email"]
    password = request.POST["password"]
    user = authenticate(request, username=email, password=password)
    
    if User.objects.filter(email=email, is_active=False).exists():
        url = reverse('verification-alert') + f'?email={email}'
        
        return redirect(url)

    if user is not None:
        login(request, user)
                
        if next_url and next_url != request.path:
            return redirect(next_url)
        
        return redirect('home')

    return render(request, 'html/authentication/login.html', {'error': f'Invalid email or password'})


def logout_view(request):
    logout(request)

    return redirect('home')


@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.method == "GET":
        return render(request, 'html/authentication/signup.html')
    
    else:   
        form = CustomUserCreationForm(request.POST)
       
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            
            username = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            # login(request, user) # don't login user unless the user has verified their email
            # send_token(username)
            # Assign free plan to the user
            try:
                plan = Plan.objects.first()
                if not plan:
                    raise Http404("Plan not found")
                # Enregistrer la souscription localement, sans paiement
                Transaction.objects.create(
                    variant='manual',
                    total=0,
                    currency='usd',
                    description=f"Free plan: {plan.name}",
                    billing_email=user.email,
                    user=user,
                    plan=plan,
                    subscription_status=SUBSCRIPTION_STATUS.ACTIVE,
                    status='confirmed'
                )

            except Exception:
                raise Exception("Something went wrong")
            
            url = reverse('verification-alert') + f'?email={username}'
            return redirect(url)

       
        return render(request, 'html/authentication/signup.html', context={'errors': form.errors})


def verification_alert(request):
    """
        alert that the user has to verify their email
    """
    email = request.GET.get('email') or ''
    return render(request, 'html/authentication/verification-alert.html', context={'from_email': settings.EMAIL_HOST,
                                                                'to_email': email   
                                                            })


@require_http_methods(["GET", "POST"])
def verification_resend(request):
    """
        resend the confirmation email
    """

    if request.method == "POST":

        email = request.POST.get('email')

        user = User.objects.filter(email=email)

        if not user.exists():

            return render(request, 'html/authentication/resend-confirmation.html', {'error': f'The email {email} is not registered'})

        if user.filter(is_active=True):
            return render(request, 'html/authentication/resend-confirmation.html', {'error': f'The email {email} is already active'})

        send_token(email)
        url = reverse('verification-alert') + f'?email={email}'
        return redirect(url)

    return render(request, 'html/authentication/resend-confirmation.html')


def verify_email(request):
    token = request.GET.get('token')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        email = payload['email']

        user = get_user_model().objects.get(email=email)
        user.is_active = True
        user.save()

        send_token(email)

        return redirect('login')  # Redirect to a success page

    except jwt.ExpiredSignatureError:
        return render(request, 'html/authentication/email-verification.html', context={'error': 'Token expired, request another'})

    except (jwt.DecodeError, Exception):
        return render(request, 'html/authentication/email-verification.html', context={'error': 'Unknown error occurred, request a new token'})
    



class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'html/authentication/password-reset-request.html'
    email_template_name = 'html/authentication/password-reset-email.html'
    # subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('password-reset')