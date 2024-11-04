from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from hello_public.models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .forms import CreateUserForm
from .forms import *

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'admin', login_url='hello_public:home')
def home_page(request):
    all_users = User.objects.all()
    official_users = User.objects.filter(userType='official')
    normal_users = User.objects.filter(userType='normal')
    moderator_users = User.objects.filter(userType='moderator')
    recent_users = User.objects.filter(date_joined__gte=timezone.now() - timezone.timedelta(hours=24))
    
    context = {
        'all_users': all_users,
        'official_users': official_users,
        'normal_users': normal_users,
        'moderator_users': moderator_users,
        'recent_users': recent_users,
    }
    
    return render(request, 'hello_admin/index.html', context)

def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.userType == 'admin':
            login(request, user)
            return redirect('hello_admin:home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'hello_admin/login.html')

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'admin', login_url='hello_public:home')
def logout_user(request):
    logout(request)
    return redirect('hello_admin:home')

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'admin', login_url='hello_public:home')
def update_role(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.userType = request.POST.get('userType')
        user.save()
        messages.success(request, f'{user.username}\'s role updated successfully')
        return redirect('hello_admin:home')

    return render(request, 'hello_admin/update_role.html', {'user': user})

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'admin', login_url='hello_public:home')
def update_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'{user.username}\'s profile updated successfully')
            return redirect('hello_admin:home')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'hello_admin/update_profile.html', {'form': form, 'user': user})

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'admin', login_url='hello_public:home')
def change_password(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UpdatePasswordForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, f'{user.username}\'s password changed successfully')
            return redirect('hello_admin:home')
    else:
        form = UpdatePasswordForm(request.user)

    return render(request, 'hello_admin/change_password.html', {'form': form, 'user': user})

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'admin', login_url='hello_public:home')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        why_delete = request.POST['why_delete']
        # send email to post owner
        subject = 'Your account has been deleted'
        message = f"{why_delete} deleted by moderator:{request.user.id}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)

        user.delete()
        return redirect('hello_admin:home')

    return render(request, 'hello_admin/delete_user.html', {'user': user})

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'admin', login_url='hello_public:home')
def ban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        why_delete = request.POST['why_delete']
        # send email to post owner
        subject = 'Your account has been deleted'
        message = f"{why_delete} deleted by admin:{request.user.id}. please contact the admin at admin@helloaiu.com."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)

        user.is_banned = True
        user.save()
        return redirect('hello_admin:home')

    return render(request, 'hello_admin/ban_user.html', {'user': user})

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'admin', login_url='hello_public:home')
def unban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    user.is_banned = False
    user.save()
    return redirect('hello_admin:home')

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'admin', login_url='hello_public:home')
def create_user(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user_type = form.cleaned_data.get('userType')

            # Create a new user
            new_user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                userType=user_type
            )

            # Render a template to display the new user's information
            context = {
                'new_user': new_user
            }
            return redirect('hello_admin:home')

    context = {
        'form': form
    }
    return render(request, 'hello_admin/create_user.html', context)


