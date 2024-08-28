from django.shortcuts import render
from app.forms import *
from django.http import HttpResponse,HttpResponseRedirect
from django.core.mail import send_mail,EmailMessage
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import authenticate,login,logout
from app.models import *
import random
from django.core.cache import cache
# Create your views here.
def register(request):
    EUFO=UserForm()
    EPFO=ProfileForm()
    d={'EUFO':EUFO,'EPFO':EPFO}
    if request.method=='POST' and request.FILES:
        NMUFO=UserForm(request.POST)
        NMPFO=ProfileForm(request.POST,request.FILES)
        if NMUFO.is_valid() and NMPFO.is_valid():
            MUFO=NMUFO.save(commit=False)
            pw=NMUFO.cleaned_data['password']
            MUFO.set_password(pw)
            MUFO.save()

            MPFO=NMPFO.save(commit=False)
            MPFO.username=MUFO
            MPFO.save()

            send_mail('Regarding Registration','Thank you For Your Registration','aahashs30@gmail.com',[MUFO.email],fail_silently=False)
            return HttpResponse('Registration Successful')
        else:
            return HttpResponse('Invalid Data')
    return render(request,'register.html',d)

def home(request):
    if request.session.get('username'):
        username=request.session.get('username')
        d={'username':username}
        return render(request,'home.html',d)
    return render(request,'home.html')

def user_login(request):
    if request.method=='POST':
        username=request.POST['un']
        password=request.POST['pw']
        AUO=authenticate(username=username,password=password)
        if AUO and AUO.is_active:
            login(request,AUO)
            request.session['username']=username
            return HttpResponseRedirect(reverse('home'))
        else:
            return HttpResponse('Invalid Credentials')
    return render(request,'user_login.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

@login_required
def display_data(request):
    username=request.session.get('username')
    if username:

        UO=User.objects.get(username=username)
        PO=Profile.objects.get(username=UO)
        d={'UO':UO,'PO':PO}
        return render(request,'display_data.html',d)
    else:
        return HttpResponse('Session Expired')

@login_required
def change_password(request):
    if request.method=='POST':
        cpw=request.POST['cpw']
        username=request.session['username']
        UO=User.objects.get(username=username)
        UO.set_password(cpw)
        UO.save()

        cache.delete(f'{username}_otp')
        return HttpResponse('Password is Changed')

    return render(request,'change_password.html')

def reset_password(request):
    if request.method=='POST':
        # pw=request.POST['pw']
        username=request.POST['un']
        LUO=User.objects.filter(username=username)
        if LUO:
            UO=LUO[0]
            # UO.set_password(pw)
            # UO.save()
            otp=random.randint(100000,999999)
            cache.set(f'{username}_otp',otp,timeout=300)
            send_mail('Reset Password','Your OTP is '+str(otp),'from@example.com',[UO.email],fail_silently=False,)
            request.session['username']=username
            return HttpResponseRedirect(reverse('verify_otp'))
        else:
            return HttpResponse('User is not present')

    return render(request,'reset_password.html')

def verify_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST['otp']
        username = request.session.get('username')
        if not username:
            return HttpResponse('Session expired, please try again.')

        # Retrieve the OTP from the cache
        otp_stored = cache.get(f'{username}_otp')

        if otp_stored and str(otp_stored) == otp_entered:
            # OTP is correct, allow password reset
            return HttpResponseRedirect(reverse('change_password'))
        else:
            return HttpResponse('Invalid OTP')

    return render(request, 'verify_otp.html')
