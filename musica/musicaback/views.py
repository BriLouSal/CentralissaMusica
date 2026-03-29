from django.shortcuts import render
import uuid

from django.shortcuts import render, redirect, reverse
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage

from django.contrib.auth.decorators import login_required

from django.contrib import messages
from .models import EmailVerificationCode, Profile
from django.core.mail import send_mail
from random import randint
from django.conf import settings
# Create your views here.
from django.db.models.signals import post_save
from django.core.cache import cache
from django.dispatch import receiver
import threading

import secrets

import json

from django.http import JsonResponse


from allauth.socialaccount.signals import social_account_added

from datetime import datetime, date

from dateutil.relativedelta import relativedelta
import requests


# Create your views here.


def send_verification_email(email, code):
    send_mail(
        subject="Verify your KentroChrema account",
        message=f"Your verification code is: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    print("SENDING VERIFICATION EMAIL")






def signup_page(request):
    print("Authenticated:", request.user.is_authenticated)
    print("User:", request.user)
    # If the user is already logged in, we'll just put them redirect them to the portfolio setting.
    if request.user.is_authenticated:
        return redirect('home')
    # Signup
    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if existing_user.is_active:
                return redirect('login')
            else:
                user = existing_user

        # Then we should redirect the user to verification code and match it email
        else:
            # We should also build an absoloute url for security purposes, 
            user = User.objects.create_user(username=username, password=password, email=email)
            # They're not verified, and they'll have to do it through the built in url
            user.is_active = False
            user.save()

            profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={'is_verified': False}
        )
            if not created:
                profile.is_verified = False
                profile.save()
            if user and user.is_active:
                return redirect("login")


        # So we wanna generate the verification code
        generated_code = f"{secrets.randbelow(1_000_000):06}"
        
        
        # After that we wanna create the model of email verification and we can do a if-statement to check if the email verification is matched with the user
        
        EmailVerificationCode.objects.update_or_create(user=user, defaults={'code': generated_code, 'is_verified': False})

        request.session['verify_user_id'] = user.id

        try:
            thread = threading.Thread(
                target=send_verification_email,
                args=(email, generated_code),
                daemon=True
            )
            thread.start()
            return redirect('verify')
        except Exception as e:
            messages.error(request, f"Email failed: {e}")
            return redirect('signup')
            

    return render(request, 'base/authentication/signup.html')


def loginpage(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)


        if user is not None:
            # check if they're veriified
            if not user.is_active:
                messages.warning(request, "Please verify your email first.")
                return redirect('verify')
            
            # Clarify backend, as there's a issue and Django complains about it
            user.backend = 'musicaback.backend.EmailBackend'
            
            login(request, user)
            
            return redirect('home')
        else:
            # Invalid password case
            messages.error(request, "Invalid password.")
            
            return redirect('login')
            
    return render(request, 'base/authentication/login.html')


@receiver(social_account_added)
def email_google_activation(request, sociallogin, **kwargs):
    # Create the account for them and create profile
    user = sociallogin.user
    # Create the profile
    profile, _ = Profile.objects.get_or_create(user=user)

    profile.is_verified = True
    profile.save()

    user.is_active = True
    user.save()

        

def logout_page(request):
    logout(request)
    return redirect('signup')



def home(request):
    print("Authenticated:", request.user.is_authenticated)
    print("User:", request.user)
    return render(request, 'base/home.html')