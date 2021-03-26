from django.shortcuts import render
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from .models import CustomUser
from . import forms

######
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from .tokens import account_activation_token


class SignUpView(CreateView):
    form_class = forms.SignupForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'django_users/register.html'

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.is_active = False
        self.object.save()

        current_site = get_current_site(self.request)
        mail_subject = 'Activate your account!'
        message = render_to_string('django_users/account_activate_email.html', {
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(self.object.pk)),
            'token': account_activation_token.make_token(self.object)
                                   })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage( mail_subject, message, to=[to_email])
        email.send()
        return super(SignUpView, self).form_valid(form)


class GoodByeView(TemplateView):
    template_name = 'bye.html'


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # return redirect('home')
        link_is_valid = True
    else:
        link_is_valid = False

    return render(request, 'django_users/acc_link_confirm.html', {'link_is_valid': link_is_valid})