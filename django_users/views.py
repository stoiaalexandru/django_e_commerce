from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView, FormView
from django.urls import reverse_lazy
from .models import CustomUser, ActivationEmailOptions
from . import forms
from django.contrib.auth.views import PasswordResetView as DjangoPasswordResetView
from django.contrib.auth.views import PasswordResetDoneView as DjangoPasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView as DjangoPasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView as DjangoPasswordResetCompleteView
######
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.utils import timezone
from .functions import send_email


class SignUpView(CreateView):
    form_class = forms.SignupForm
    success_url = reverse_lazy('django_users:register_success')
    template_name = 'django_users/register.html'

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.is_active = False
        self.object.activation_mail_date = timezone.now()
        self.object.save()

        current_site = get_current_site(self.request)
        # mail_subject = 'Activate your account!'
        # message = render_to_string('django_users/account_activate_email.html', {
        #     'domain': current_site.domain,
        #     'uid': urlsafe_base64_encode(force_bytes(self.object.pk)),
        #     'token': account_activation_token.make_token(self.object)
        #                            })
        # to_email = form.cleaned_data.get('email')
        # email = EmailMessage( mail_subject, message, to=[to_email])
        # email.send()
        send_email(template='django_users/account_activate_email.html',
                   domain=current_site.domain,
                   user=self.object,
                   to_email=form.cleaned_data.get('email'))

        return super(SignUpView, self).form_valid(form)


class GoodByeView(TemplateView):
    template_name = 'bye.html'


class RegisterSuccessView(TemplateView):
    template_name = 'django_users/register_success.html'


class ActivateAccountView(TemplateView):
    template_name = 'django_users/acc_link_confirm.html'

    def get(self, request, *args, **kwargs):
        uidb64 = kwargs['uidb64']
        token = kwargs['token']
        email_settings = ActivationEmailOptions()
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
        if user is not None \
                and account_activation_token.check_token(user, token) \
                and user.activation_mail_date + email_settings.expiration_time > timezone.now():
            user.is_active = True
            user.save()
            link_is_valid = True
        else:
            link_is_valid = False
        kwargs['link_is_valid'] = link_is_valid
        return super(ActivateAccountView, self).get(request, *args, **kwargs)


class ResendActivationEmailView(FormView):
    template_name = 'django_users/resend_activation_email.html'
    form_class = forms.ResendActivationEmailForm
    success_url = reverse_lazy('django_users:resend_activation_email_success')

    def form_valid(self, form):

        user = form.cleaned_data['user']

        current_site = get_current_site(self.request)
        send_email(template='django_users/account_activate_email.html',
                   domain=current_site.domain,
                   user=user,
                   to_email=form.cleaned_data.get('email'))
        user.activation_mail_date = timezone.now()
        user.save()

        return super(ResendActivationEmailView, self).form_valid(form)


class ResendActivationEmailSuccess(TemplateView):
    template_name = 'django_users/resend_activation_email_success.html'


class PasswordResetView(DjangoPasswordResetView):
    template_name = 'django_users/registration/password_reset.html'
    email_template_name = 'django_users/registration/password_reset_email.html'
    success_url = reverse_lazy('django_users:password_reset_done')


class PasswordResetDoneView(DjangoPasswordResetDoneView):
    template_name = 'django_users/registration/password_reset_done.html'


class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    template_name = 'django_users/registration/password_reset_confirm.html'
    success_url = reverse_lazy('django_users:password_reset_complete')


class PasswordResetCompleteView(DjangoPasswordResetCompleteView):
    template_name = 'django_users/registration/password_reset_complete.html'

