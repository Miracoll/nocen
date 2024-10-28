from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from random import randrange
import secrets

from account.decorators import allowed_users
from hostel.functions import createLog, getIp, sendEmail
from .models import Log, User

# Create your views here.

class LoginForm(View):
    template_name = 'account/login.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    def post(self, request, *args, **kwargs):
        email = self.request.POST.get('email')
        password =self. request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        print(user)
    
        if user is not None:
            login(request,user)
            User.objects.filter(email=user.email).update(last_login_ip=getIp(request))
            createLog('User successfully logged in', True, user)
            return redirect('home')
        else:
            messages.error(request,'Incorrect username or password')
            return redirect('login')

def logoutuser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def addUser(request):
    # createLog('User viewed admin add user page', True, request.user)
    if request.method == 'POST':
        createLog('User started new user entry', True, request.user)
        name = request.POST.get('last')
        first_name = request.POST.get('first')
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            createLog('User entry failed due to email duplicate', False, request.user)
            messages.error(request, f'{email} already exist')
            return redirect('add-user')

        username = name
        role = 'user'
        password = str(secrets.randbelow(1000000)).zfill(4)
        while User.objects.filter(username=username).exists():
            username = username.lower() + str(randrange(1,987654))

        user = User.objects.create_user(username,email,password)
        user.is_staff = True
        user.is_superuser = False
        user.role = role
        user.last_name = name
        user.first_name = first_name
        user.is_active = True
        user.save()

        # Send mail to user
        sendEmail(email, 'Access Granted', user, password)
        createLog('Email sent to the new user', True, request.user)

        if not Group.objects.filter(name=role).exists():
            Group.objects.create(name=role)
        getgroup = Group.objects.get(name=role)
        getgroup.user_set.add(user.id)
        
        createLog('Registration successful', True, request.user)
        messages.success(request, 'Done')
        return redirect('add-user')
    return render(request, 'hostel/add-user.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def manageUser(request):
    # createLog('User view manage user page', True, request.user)
    users = User.objects.all()
    logs = Log.objects.all()
    context = {'users':users,'logs':logs}
    return render(request, 'hostel/manage-user.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def disableUser(request,user):
    User.objects.filter(email=user).update(is_active=False)
    createLog(f'Disabled <user:{user}>', True, request.user)
    messages.success(request, 'Done')
    return redirect('manage-user')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def enableUser(request,user):
    User.objects.filter(email=user).update(is_active=True)
    createLog(f'Enabled <user:{user}>', True, request.user)
    messages.success(request, 'Done')
    return redirect('manage-user')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','user'])
def changePassword(request):
    if request.method == 'POST':
        pass0 = request.POST.get('pass')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        user = User.objects.get(username=request.user.username)
        if not user.check_password(pass0):
            messages.error(request,'incorrect password')
            return redirect('change-password')
        
        if not pass1 == pass2:
            messages.error(request, 'Password did not match')
            return redirect('change-password')
        if len(str(pass1)) < 7:
            messages.error(request, 'Password length should be at least 7')
            return redirect('change-password')
        
        u = User.objects.get(username=request.user.username)
        u.set_password(pass1)
        u.save()
        # user = authenticate(request, username=request.user.username, password=pass1)
        messages.success(request, 'Password changed successfully')
        return redirect('logout')
            
    return render(request, 'hostel/change-password.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def startNewSession(request):
    return render(request, 'hostel/start-session.html')