from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from itertools import chain
from django.db.models import OuterRef, Subquery, Max
from hello_public.models import *

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'moderator', login_url='hello_public:home')
def home_page(request):
    posts = Post.objects.filter(postStatus='live')
    activities = Activity.objects.all()

    recent_posts = Post.objects.filter(postDate__gte=timezone.now()-timezone.timedelta(hours=24), postStatus='live')
    recent_activities = Activity.objects.filter(activityCreateDate__gte=timezone.now()-timezone.timedelta(hours=24))

    recent_posts_and_activities = recent_posts.union(recent_activities)
    recent_posts_and_activities = recent_posts_and_activities.order_by('-postDate')
    # recent_items = sorted(chain(recent_posts, recent_activities), key=lambda item: item.postDate or item.activityCreateDate, reverse=True)

    context = {
        'posts': posts, 
        'activities': activities, 
        'recent_posts': recent_posts, 
        'recent_activities': recent_activities,
        'recent_items': recent_posts_and_activities
    }
    return render(request, 'hello_moderator/index.html', context)


def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.userType == 'moderator':
            login(request, user)
            return redirect('hello_moderator:home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'hello_moderator/login.html')

@login_required(login_url='hello_moderator:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'moderator', login_url='hello_public:home')
def logout_user(request):
    logout(request)
    return redirect('hello_moderator:home')

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'moderator', login_url='hello_public:home')
# def all_post(request):
#     all_post = Post.objects.all()
#     live_posts = Post.objects.filter(postStatus='live').order_by('-postDate')
#     draft_posts = Post.objects.filter(postStatus='draft').order_by('-postDate')
#     anonymous_posts = Post.objects.filter(postType='anonymous').order_by('-postDate')
#     bin_posts = Post.objects.filter(postStatus='in_bin').order_by('-postDate')
#     ban_posts = Post.objects.filter(postStatus='ban').order_by('-postDate')
#     recent_posts = Post.objects.filter(postDate__gte=timezone.now()-timezone.timedelta(hours=24), postStatus='live')

#     reported_posts = # here

#     print("report posts",reported_posts)

#     context = {
#         'all_post': all_post,
#         'live_posts': live_posts,
#         'draft_posts': draft_posts,
#         'bin_posts': bin_posts,
#         'anonymous_posts': anonymous_posts,
#         'recent_posts': recent_posts, 
#         'ban_posts': ban_posts, 
#         'reported_post': reported_posts,
#     }
#     return render(request, 'hello_moderator/all_post.html', context)

def all_post(request):
    all_post = Post.objects.all()
    live_posts = Post.objects.filter(postStatus='live').order_by('-postDate')
    draft_posts = Post.objects.filter(postStatus='draft').order_by('-postDate')
    anonymous_posts = Post.objects.filter(postType='anonymous').order_by('-postDate')
    bin_posts = Post.objects.filter(postStatus='in_bin').order_by('-postDate')
    ban_posts = Post.objects.filter(postStatus='ban').order_by('-postDate')
    recent_posts = Post.objects.filter(postDate__gte=timezone.now()-timezone.timedelta(hours=24), postStatus='live')

    subquery = ReportPost.objects.values('postId').annotate(latest_created=Max('created_at'))
    reported_posts = ReportPost.objects.filter(created_at__in=subquery.values('latest_created')).order_by('-created_at')

    print(reported_posts)

    context = {
        'all_post': all_post,
        'live_posts': live_posts,
        'draft_posts': draft_posts,
        'bin_posts': bin_posts,
        'anonymous_posts': anonymous_posts,
        'recent_posts': recent_posts, 
        'ban_posts': ban_posts, 
        'reported_posts': reported_posts,
    }
    return render(request, 'hello_moderator/all_post.html', context)

from django.db.models import Count
@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'moderator', login_url='hello_public:home')
def all_activities(request):
    activities = Activity.objects.annotate(num_participants=Count('activityparticepationlist')).all().order_by('-activityCreateDate')
    # num_participants = ActivityParticepationList.objects.values('activityId').annotate(num_participants=Count('userId'))
    recent_activities = Activity.objects.filter(activityCreateDate__gte=timezone.now()-timezone.timedelta(hours=24))
    locations = ActivityLocation.objects.all()
    # print(recent_activities)
    context = {
        'activities': activities,
        'recent_activities': recent_activities,
        'locations': locations,
    }
    return render(request, 'hello_moderator/activities.html', context)


# POST ACTIONS
@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'moderator', login_url='hello_public:home')
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        why_delete = request.POST['why_delete']
        # send email to post owner
        subject = 'Your post has been deleted'
        message = f"{why_delete} deleted by moderator:{request.user.id}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [post.userId.email]
        send_mail(subject, message, from_email, recipient_list)

        # delete post
        post.postStatus = 'in_bin'
        post.postDate = timezone.now()
        post.save()
        return redirect('hello_moderator:posts')

    return render(request, 'hello_moderator/delete_post.html', {'post': post})

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'moderator', login_url='hello_public:home')
def approve_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.postStatus = 'live'
        post.approveBy = request.user
        post.postDate = timezone.now()
        post.save()
        return redirect('hello_moderator:posts')
    except Post.DoesNotExist:
        return redirect('hello_moderator:posts')
    
@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'moderator', login_url='hello_public:home')
def ban_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        why_delete = request.POST['why_delete']
        # send email to post owner
        subject = 'Your post has been ban'
        message = f"{why_delete} ban by moderator:{request.user.id}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [post.userId.email]
        send_mail(subject, message, from_email, recipient_list)

        # delete post
        post.postStatus = 'ban'
        # post.postDate = timezone.now()
        post.save()
        return redirect('hello_moderator:posts')

    return render(request, 'hello_moderator/ban_post.html', {'post': post})
    
@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'moderator', login_url='hello_public:home')
def unban_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.postStatus = 'live'
        post.approveBy = request.user
        post.save()
        return redirect('hello_moderator:posts')
    except Post.DoesNotExist:
        return redirect('hello_moderator:posts')
    
@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'moderator', login_url='hello_public:home')
def disable_comment_on_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        why_delete = request.POST['why_delete']
        # send email to post owner
        subject = 'Command disable'
        message = f"{why_delete} Disable by moderator:{request.user.id}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [post.userId.email]
        send_mail(subject, message, from_email, recipient_list)

        # delete post
        post.disable_comment = True
        # post.postDate = timezone.now()
        post.save()
        return redirect('hello_moderator:posts')

    return render(request, 'hello_moderator/disable_command.html', {'post': post})
    
@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'moderator', login_url='hello_public:home')
def enable_comment_on_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.disable_comment = False
        post.save()
        return redirect('hello_moderator:posts')
    except Post.DoesNotExist:
        return redirect('hello_moderator:posts')

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'moderator', login_url='hello_public:home')
def report_detail(request, post_id):
    reports = ReportPost.objects.filter(postId = post_id)
    post = get_object_or_404(Post, id=post_id)
    images = Image.objects.filter(postId=post)

    context = {
        'reports': reports,
        'post': post,
        'images': images,
    }
    return render(request, 'hello_moderator/report_detail.html', context)

@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'moderator', login_url='hello_public:home')
def delete_report(request, report_id):
    report = ReportPost.objects.get(pk = report_id)
    report.delete()
    return redirect('hello_moderator:report_detail' )
  
# ACTIVITY ACTIONS
@login_required(login_url='hello_public:login')
@user_passes_test(lambda user: user.is_authenticated and user.userType == 'moderator', login_url='hello_public:home')
def delete_activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)

    if request.method == 'POST':
        why_delete = request.POST['why_delete']
        # send email to post owner
        subject = 'Your activity has been deleted'
        message = f"{why_delete} deleted by moderator:{request.user.id}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [activity.activityOrganizer.email]
        send_mail(subject, message, from_email, recipient_list)

        # delete post
        activity.delete()
        return redirect('hello_moderator:activities')

    return render(request, 'hello_moderator/delete_activity.html', {'activity': activity})

