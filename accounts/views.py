from django.shortcuts import redirect, render
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from base.functions import *
from accounts.forms import *
from .models import User
# Create your views here.
@timer
def signin(request):
    if request.method=="POST":
        form = UserSignInForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username = username,password=password)
        print(user)
        if user is not None:
            login(request,user)
            return redirect('index')
        return render(request,'accounts/signin.html',{'form':form})
    form = UserSignInForm()
    return render(request,'accounts/signin.html',{'form':form})
@timer
def signup(request):
    if request.method=="POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            messages.success(request,"here")
            signed_user = form.save()
            login(request,signed_user)
            return redirect('index')
        context = {'form':form}
        return render(request,'accounts/signup.html',context)
    form = UserSignInForm()
    context = {'form':form}
    return render(request,'accounts/signup.html',context)

@login_required
def signout(request):
    logout(request)
    return redirect('index')


def idfinder(request):
    if request.method == 'POST':
        # messages.success(request, request.POST.get('email'))
        email = request.POST.get('email')
        if email == '':
            messages.warning(request,'Email을 입력 해 주세요')
            return render(request, 'accounts/idfinder.html')
        try:
            user = User.objects.get(email=email)
            messages.success(request,f"ID : {user.username}")
        except:
            messages.error(request,'회원 정보가 없어요')
            return render(request, 'accounts/idfinder.html')
        return redirect('accounts:signin')
    return render(request, 'accounts/idfinder.html')