from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import login
from .models import *
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from base.models import *


def SignIn(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = authenticate(request, username=username, password=password)
        except Exception as e:
            print(e)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')



def SignUp(request):
    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        username = request.POST.get('username')
        password = request.POST.get('password')
                
        if User.objects.filter(username=username).exists():
            print(request, 'Username already exists.')

        else:
            user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
            )
            print("Account Creation Done")
            user.save()
            login(request, user)
            return redirect('home')  
        

    return render(request, 'signup.html')


def LogOut(request):
    logout(request)
    print("Log Out Successfully")
    return redirect('SignIn')


def Home(request):
    blogs = Post.objects.all()
    context = {
        'posts' : blogs
    }
    return render(request, 'index.html', context)