import users
from django.contrib import messages
from .forms import UserRegisterForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, request
from django.db import transaction
import stripe
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .models import *
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from .forms import UserCreationForm, UserUpdateForm, ProfileUpdateForm
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
import jwt
from .utils import Util

'''
def registerPage(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You will now be able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})
'''
def registerPage(request):
    if(request.method == 'POST'):
        form = UserRegisterForm(request.POST)
        if(form.is_valid()):
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            user = User.objects.get(username=username)
            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request).domain
            relativeLink = reverse('login')
            absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
            email_body = 'Greetings, \n Hey '+user.username+', use the link below to verify your email. If you have not requested for an account verification, you can safely ignore this email. \n'+absurl+'\n Regards, \n First Draft'
            data = {
                'to': email,
                'email_body': email_body,
                'email_subject': 'Verify your email'
            }
            Util.send_email(data)
            return redirect('active_email')
    else :
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})

def verify_email_page(request):
    return render(request, 'users/active_email.html')


def verifyEmail(request):
    token = request.GET.get('token')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
        user = User.objects.get(id=payload['user_id'])
        if not user.is_authenticated:
            user.is_authenticated = True
            user.save()
        messages.success(request, f'Your Account has been Authenticated! You can now Login {user.username}!')
        return redirect('login')

    except jwt.ExpiredSignatureError as expired:
        return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST, template_name='blah.html')

    except jwt.exceptions.DecodeError as invalid:
        return Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)

    except :
        return Response({'error': 'Error'}, status=status.HTTP_400_BAD_REQUEST)



@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)
