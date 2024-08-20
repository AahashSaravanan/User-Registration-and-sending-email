from django.shortcuts import render
from app.forms import *
from django.http import HttpResponse
from django.core.mail import send_mail
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