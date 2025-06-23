from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email", )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password2')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("email",)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone_number', 'company_name', 'activity_area', 'prompt_personalization']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'tw-input tw-text-black tw-w-full tw-rounded tw-border tw-py-2 tw-px-3'}),
            'company_name': forms.TextInput(attrs={'class': 'tw-input tw-text-black tw-w-full tw-rounded tw-border tw-py-2 tw-px-3'}),
            'activity_area': forms.Select(attrs={'class': 'tw-select tw-text-black tw-w-full tw-rounded tw-border tw-py-2 tw-px-3'}),
            'prompt_personalization': forms.Textarea(attrs={'class': 'tw-textarea tw-text-black tw-w-full tw-rounded tw-border tw-py-2 tw-px-3'}),
        }
