from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.utils import timezone

from .models import CustomUser, ActivationEmailOptions


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('email',)


class SignupForm(CustomUserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')


class ResendActivationEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email_settings = ActivationEmailOptions()
        email = self.cleaned_data.get('email')
        try:
            user = CustomUser.objects.get(email__iexact=email)
        except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise forms.ValidationError('The user does not exist')

        if user.activation_mail_date + email_settings.resend_delay > timezone.now():
            raise forms.ValidationError(
                'You have to wait {} until requesting another mail.'.format((user.activation_mail_date +
                                                                            email_settings.resend_delay-timezone.now())))
        if user.is_active:
            raise forms.ValidationError('This user is already active, please LOGIN instead!')

        self.cleaned_data['user'] = user
        return email

