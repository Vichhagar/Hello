from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
import json
import hashlib
from .forms import *
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core import serializers
from django.template.defaultfilters import timesince
from django.http import HttpResponseForbidden

# async def send_notification(user_id, notification_type):
#     print('send notification')
#     print(f'user_id: {user_id}')
#     print(f'notification type: {user_id}')
#     message = {
#         'type': 'notification',
#         'message': {
#             'notification_type': notification_type
#         }
#     }
#     channel_layer = get_channel_layer()
#     await channel_layer.group_send(f'user_{user_id}', message)

def create_notification(notificationLink, notificationSender, notificationReceiver, notificationOn, notificationType):
    Notification.objects.create(
        # post=post,
        notificationLink = notificationLink,
        notificationSender = notificationSender,
        notificationReceiver = notificationReceiver,
        notificationOn = notificationOn,
        notificationType = notificationType,
        notificationStatus = 'unread'
    )

# @login_required(login_url='hello_public:login')
# def home_page(request):
#     current_time = datetime.now()
#     active_activities = Activity.objects.filter(
#             # Q(activityOpenDate__lte=current_time) &
#             Q(activityCloseDate__gt=current_time) &
#             Q(activityDate__gt=current_time)
#         ).order_by('-activityCreateDate')[:5]
#     live_posts = Post.objects.filter(postStatus='live').prefetch_related('image_set').select_related('userId').order_by('-postDate')

#     for post in live_posts:
#         post.num_likes = post.like_set.count()
#         post.num_comments = post.comment_set.count()
#         post.num_saves = post.save_set.count()
#         post.user_has_liked = post.like_set.filter(userId=request.user).exists()
#         post.user_has_saved = post.save_set.filter(userId=request.user).exists()

#     context = {
#         'live_posts': live_posts,
#         'active_activities': active_activities
#     }
    
#     return render(request, 'hello_public/index.html', context)

from django.utils import timezone

@login_required(login_url='hello_public:login')
def home_page(request):
    current_time = timezone.now()
    active_activities = Activity.objects.filter(
            # Q(activityOpenDate__lte=current_time) &
            Q(activityCloseDate__gt=current_time) &
            Q(activityDate__gt=current_time)
        ).order_by('-activityCreateDate')[:5]
    live_posts = Post.objects.filter(postStatus='live').prefetch_related('image_set').select_related('userId').order_by('-postDate')
    

    for post in live_posts:
        post.num_likes = post.like_set.count()
        post.num_comments = post.comment_set.count()
        post.num_saves = post.save_set.count()
        post.user_has_liked = post.like_set.filter(userId=request.user).exists()
        post.user_has_saved = post.save_set.filter(userId=request.user).exists()

        reported_post_exists = bool(ReportPost.objects.filter(postId=post.id).first())
        post.is_reported = reported_post_exists

    # Calculate time since activity create
    for activity in active_activities:
        time_since_create = current_time - activity.activityCreateDate
        activity.time_since_create_hours = time_since_create.total_seconds() // 3600

    context = {
        'live_posts': live_posts,
        'active_activities': active_activities
    }
    
    return render(request, 'hello_public/index.html', context)

def login_page(request):
    if request.user.is_authenticated:
        return redirect('hello_public:home')
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_banned == False:
                    messages.info(request, "username or password is wrong")

                    login(request, user)
                    return redirect('hello_public:home')
                messages.info(request, "You are banned from the system")
            else:
                messages.info(request, "username or password is wrong")
                
        context = {}
        return render(request, 'hello_public/login.html', context)

@login_required(login_url='hello_public:login')
def logout_user(request):
    logout(request)
    return redirect('hello_public:login')

def request_account(request):
    if request.method == 'POST':
        email = request.POST['email']
        # if not email.endswith('.apiu.edu'):
        #     messages.error(request, 'Only email addresses ending with ".apiu.edu" are allowed.')
        #     return render(request, 'hello_public/requestAccount.html')
        
        hashed_email = hashlib.sha256(email.encode('utf-8')).hexdigest()

        # Check if email is already used or exists in the database
        if RegistrationToken.objects.filter(hashed_email=hashed_email, used=False).exists():
            messages.info(request, "A registration link has already been sent to this email.")

        elif RegistrationToken.objects.filter(hashed_email=hashed_email, used=True).exists():
            messages.info(request, "This email has already been used to register.")

        else:
            token = RegistrationToken(hashed_email=hashed_email)
            token.save()

            link = request.build_absolute_uri('/') + f'register/?token={token.token}&email={email}'
            subject = 'Registration link for your account'
            message = f'Use the following link to register: {link}'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)

            messages.info(request, "The registration link has been sent to your email.")
    return render(request, 'hello_public/requestAccount.html')

def register(request):
    token = request.GET.get('token')
    try:
        registration_token = RegistrationToken.objects.get(token=token, used=False)
    except RegistrationToken.DoesNotExist:
        # Invalid token or already used
        # to error page telling that the token is already in use
        # return render(request, 'registration/register_error.html')
        return
    
    # get_email = RegistrationToken.objects.filter(token=token).values_list('hashed_email', flat=True).first()

    if request.method == 'POST':
        form = CreateUserForm()
        form = CreateUserForm(request.POST, files=request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.email = request.GET.get('email')
            instance.save()

            # messages.success(request, "Account created")

            # Mark token as used
            registration_token.used = True
            registration_token.save()

            return redirect('hello_public:login')
        else:
            error_messages = []
            for field, errors in form.errors.items():
                error_messages.append(f" {', '.join(errors)}")
            context = {'form': form, 'messages': error_messages}
            return render(request, 'hello_public/register.html', context)

        # if form.errors:
        #     error_messages = []
        #     for field, errors in form.errors.items():
        #         error_messages.append(f"{field.capitalize()}: {', '.join(errors)}")
        #     context = {'form': form, 'messages': error_messages}
        #     return render(request, 'hello_public/register.html', context)

        #to home page
        # return redirect('registration_complete')
    #change
    return render(request, 'hello_public/register.html')

@login_required(login_url='hello_public:login')
def create_post(request):
    if request.method == 'POST':
        # create a form for the post
        post_form = PostForm(request.POST or None)
        # create a formset for the images
        # ImageFormSet = inlineformset_factory(Post, Image, fields=('imageLink',), extra=3, max_num=10)
        images_form = ImageForm(request.FILES or None)
        images = request.FILES.getlist('post_image')

        is_draft = request.POST.get('policy_check_box', False)
        if is_draft:
            post_status = 'draft'
            post_type = 'anonymous'
        else:
            post_status = 'live'
            post_type = 'normal'

        if post_form.is_valid():
            # save the post and formset if valid
            post = post_form.save(commit=False)
            post.userId = request.user
            post.postStatus = post_status
            post.postType = post_type
            post.save()

            if request.user.userType == 'official' and post_type != 'anonymous':
                # get all users who are not in the IgnoreNotification table
                ignore_users = IgnoreNotification.objects.filter(user=request.user).values_list('ignored_by', flat=True)
                all_users = User.objects.exclude(id__in=ignore_users)

                # create notification for all users who are not ignored
                for user in all_users:
                    if user != request.user:
                        create_notification(post.id,request.user,user,"post","new_post")

        for image in images:
            new_image = Image(postId=post, imageLink=image)
            new_image.save()
            # image_formset.instance = post
            # image_formset.save()

        return redirect('hello_public:home')
        
    return render(request, 'hello_public/createPost.html')

@login_required(login_url='hello_public:login')
def post_detail(request, post_id):
    # Get the post object with the specified id, or return a 404 error if it doesn't exist
    post = get_object_or_404(Post, id=post_id)

    # Check if the post is live, and if not, only allow moderators to view
    if post.postStatus != 'live' and request.user.userType != 'moderator':
        print("not allow")
        return HttpResponseForbidden()

    # Get related objects (images, likes, comments, saves) for the post
    images = Image.objects.filter(postId=post)
    likes = Like.objects.filter(postId=post)
    comments = Comment.objects.filter(postId=post).order_by('-conmmentTime')
    saves = Save.objects.filter(postId=post)

    # Add additional information about the post
    post.num_likes = post.like_set.count()
    post.num_comments = post.comment_set.count()
    post.num_saves = post.save_set.count()
    post.user_has_liked = post.like_set.filter(userId=request.user).exists()
    post.user_has_saved = post.save_set.filter(userId=request.user).exists()

    # Handle comment submission
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.userId = request.user
            comment.postId = post
            comment.save()

            if comment.postId.userId != request.user:
                create_notification(comment.postId.id, request.user, comment.postId.userId, "post", "comment")

            return JsonResponse({'success': True, 'comment_id': comment.id})
        else:
            return JsonResponse({'success': False, 'errors': comment_form.errors})
    else:
        comment_form = CommentForm()

    # Create context dictionary
    context = {
        'post': post,
        'images': images,
        'likes': likes,
        'comments': comments,
        'saves': saves,
        'comment_form': comment_form,
    }

    # Render the template with context
    return render(request, 'hello_public/post_detail_1.html', context)

@login_required(login_url='hello_public:login')
def add_reply(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == 'POST':
        reply_form = ReplyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.userId = request.user
            reply.conmmentId = comment
            reply.save()

            if comment.userId != request.user:
                create_notification(comment.postId.id, request.user, comment.userId, "post", "reply")

            return JsonResponse({'success': True, 'reply_id': reply.id})
            # return redirect('hello_public:post_detail', post_id=post.id)
        else:
            return JsonResponse({'success': False, 'errors': reply_form.errors})

@login_required(login_url='hello_public:login')
def add_like(request, post_id):
    # Get the Post object with the specified ID
    post = get_object_or_404(Post, id=post_id)

    try:
        # Check if a Like object already exists for this user and post
        like = Like.objects.get(postId=post, userId=request.user.id)
        like.delete()  # Delete the existing Like object
        return JsonResponse({'success': True})
    except Like.DoesNotExist:
        # Create a new Like object
        like = Like(postId=post, userId=request.user)
        like.save()

        # Create a notification for the post owner
        if post.userId != request.user:
            create_notification(post.id, request.user, post.userId, "post", "like")

            # send notification to post owner
        # if request.user != post.userId:

        #     channel_layer = get_channel_layer()
        #     async_to_sync(channel_layer.group_send)(
        #         'notifications',
        #         {
        #             'type': 'notification.message',
        #             'message': f"{request.user.username} liked your post '{post.postText}'"
        #         }
        #     )

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='hello_public:login')
def add_save(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    try:
        # Check if the logged-in user has already saved the post
        save = Save.objects.get(postId=post, userId=request.user)
        save.delete()  # If yes, then delete the save
        saved = False
    except Save.DoesNotExist:
        # If no, then create a new save
        Save.objects.create(postId=post, userId=request.user)
        saved = True

    # Update the num_saves field of the post
    post.num_saves = post.save_set.count()
    post.save()

    return JsonResponse({'success': True, 'saved': saved})

@login_required(login_url='hello_public:login')
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST':
        new_text = request.POST.get('new_text')
        comment.commmentText = new_text
        comment.isEdited = True
        comment.save()
        edited_successfully = True
        data = {'success': edited_successfully}
        return JsonResponse(data)
    elif request.method == 'GET':
        data = {
            'id': comment.id,
            'text': comment.commmentText,
            'edited': comment.isEdited,
            'created_at': comment.conmmentTime,
            'post_id': comment.postId.id,
            'user_id': comment.userId.id,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request method.'})
    
@login_required(login_url='hello_public:login')
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST':
        comment.delete()
        data = {'success': True}
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request method.'})
    
@login_required(login_url='hello_public:login')
def edit_reply(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    if request.method == 'POST':
        new_text = request.POST.get('new_text')
        reply.replyText = new_text
        reply.isEdited = True
        reply.save()
        edited_successfully = True
        data = {'success': edited_successfully}
        return JsonResponse(data)
    elif request.method == 'GET':
        data = {
            'id': reply.id,
            'text': reply.replyText,
            'edited': reply.isEdited,
            'created_at': reply.replyTime,
            'comment_id': reply.conmmentId.id,
            'user_id': reply.userId.id,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request method.'})
    
@login_required(login_url='hello_public:login')
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    if request.method == 'POST':
        reply.delete()
        data = {'success': True}
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request method.'})
    
from .forms import EditPostForm
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, userId=request.user)
    if request.method == 'POST':
        post.postText = request.POST.get('postText')
        images = request.FILES.getlist('post_image')
        if request.FILES.get('post_image'):
            for image in images:
                new_image = Image(postId=post, imageLink=image)
                new_image.save()
            # create a new Image instance for the uploaded image
            # image = Image.objects.create(imageLink=request.FILES['post_image'], postId=post)
        # check which images should be removed
        for image in post.image_set.all():
            if request.POST.get(str(image.id)+'_remove'):
                image.delete()
        post.save()
        return redirect('hello_public:user_dashboard')
    else:
        images = Image.objects.filter(postId=post)
        context = {
            'post': post,
            'images': images,
        }
        return render(request, 'hello_public/edit_post.html', context)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.userId:
        return redirect('hello_public:home')
    if request.method == 'POST':
        post.postStatus = 'in_bin'
        post.postDate = timezone.now()
        post.save()
        # messages.success(request, 'This post has been moved to the recycle bin.')
        return redirect('hello_public:user_dashboard')
    return render(request, 'hello_public/delete_post.html', {'post': post})

from django.db.models import F
# ACTIVITY SECTION
@login_required(login_url='hello_public:login')
def create_activity(request):
    form = ActivityForm(request.POST or None)
    if form.is_valid():
        activity = form.save(commit=False)
        activity.activityOrganizer = request.user

        # Check if activity location is already in ActivityLocation table
        location_name = activity.activityLocation.lower().strip()
        activity_location, created = ActivityLocation.objects.get_or_create(location_name=location_name)

        # If activity location was just created, set frequency to 1
        if created:
            activity_location.frequency = 1
        else:
            # Otherwise, increment the frequency of the activity location in the ActivityLocation table
            activity_location.frequency = F('frequency') + 1

        activity_location.save()

        # Check that close date is after open date
        if activity.activityCloseDate <= activity.activityOpenDate:
            form.add_error('activityCloseDate', 'Close date must be after open date.')
            return render(request, 'hello_public/create_activity.html', {'form': form})

        # Check that activity date is after close date
        if activity.activityDate <= activity.activityCloseDate:
            form.add_error('activityDate', 'Activity date must be after close date.')
            return render(request, 'hello_public/create_activity.html', {'form': form})

        activity.save()
        return redirect('hello_public:activity_detail', pk=activity.pk)
    return render(request, 'hello_public/create_activity.html', {'form': form})

@login_required(login_url='hello_public:login')
def edit_activity(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.activityOrganizer = request.user
            activity.save()
            return redirect('hello_public:user_dashboard')
        else:
            print(form.errors)  # Debugging statement
    else:
        form = ActivityForm(instance=activity)
    context = {'form': form, 'activity': activity}
    return render(request, 'hello_public/activity_edit.html', context)

@login_required(login_url='hello_public:login')
def join_activity(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    participation, created = ActivityParticepationList.objects.get_or_create(userId=request.user, activityId=activity)

    if activity.activityOrganizer != request.user:
        create_notification(activity.id, request.user, activity.activityOrganizer, "activity", "activity_join")

    if not created:
        # The user is already participating in the activity
        return JsonResponse({'success': False})
    return JsonResponse({'success': True})

@login_required(login_url='hello_public:login')
def leave_activity(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    participation = get_object_or_404(ActivityParticepationList, userId=request.user, activityId=activity)
    participation.delete()
    return JsonResponse({'success': True})

@login_required(login_url='hello_public:login')
def activity_list(request):
    current_time = datetime.now()
    # activityOpenDate__lte=current_time,
    activities = Activity.objects.filter(
                                          activityCloseDate__gt=current_time,
                                          activityDate__gt=current_time).order_by('-activityCreateDate')
    
    user = request.user
    activities_hosted = activities.filter(activityOrganizer=user)
    activities_joined = activities.filter(activityparticepationlist__userId=user)


    for activity in activities:
        participants = ActivityParticepationList.objects.filter(activityId=activity)[:5]
        num_participants = ActivityParticepationList.objects.filter(activityId=activity).count() - 5
        

        if num_participants >= 0:
            activity.participants = list(participants)
            activity.num_participants = num_participants
        else:
            activity.participants = participants
        
        activity.user_has_joined = activity.activityparticepationlist_set.filter(userId=user).exists()
    
    context = {
        'activities': activities,
        'activities_hosted': activities_hosted,
        'activities_joined': activities_joined,
        'activities_count': activities.count(),
        'activities_hosted_count': activities_hosted.count(),
        'activities_joined_count': activities_joined.count(),
    }

    return render(request, 'hello_public/activity_list.html', context)

@login_required(login_url='hello_public:login')
def activity_detail(request, pk):
    # Retrieve the activity object with the given ID, or return a 404 error
    activity = get_object_or_404(Activity, pk=pk)
    
    # Check if the current user has already participated in this activity
    already_participated = ActivityParticepationList.objects.filter(activityId=activity, userId=request.user).exists()
    
    # Retrieve the list of users who have participated in this activity
    participation_list = ActivityParticepationList.objects.filter(activityId=activity)
    
    # Retrieve the discussion messages associated with this activity
    discussion_messages = Discussion.objects.filter(activityId=activity.id)
    
    # Prepare the context data to be passed to the template
    context = {
        'activity': activity,
        'participation_list': participation_list,
        'discussion_messages': discussion_messages,
        'already_participated': already_participated,
    }
    
    # Render the template with the context data
    return render(request, 'hello_public/activity_detail.html', context)

@login_required(login_url='hello_public:login')
def add_discussion_message(request, activity_id):
    # Retrieve the activity object with the given ID, or return a 404 error
    activity = get_object_or_404(Activity, pk=activity_id)
    
    # Retrieve the discussion room associated with this activity
    # discussion_room, created = DiscussionRoom.objects.get_or_create(roomName=f'activity_{activity.id}')
    
    # Process the form data if this is a POST request
    if request.method == 'POST':
        message = request.POST.get('message', '')
        
        # Create a new discussion message object and save it to the database
        new_message = Discussion.objects.create(
            message=message,
            userId=request.user,
            activityId=activity
        )
        new_message.save()
        
        # Return a JSON response indicating success
        return JsonResponse({'success': True})
    
    # Return a JSON response indicating failure
    return JsonResponse({'success': False})

from django.http import Http404
@login_required
def delete_activity(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if activity.activityOrganizer != request.user:
        raise Http404("You don't have permission to delete this activity.")
    if request.method == 'POST':
        activity.delete()
        # messages.success(request, 'Activity deleted successfully.')
        return redirect('hello_public:user_dashboard')
    return render(request, 'hello_public/delete_activity.html', {'activity': activity})

# USER DASHBOARD
@login_required(login_url='hello_public:login')
def user_dashboard(request):
    user = request.user
    current_time = datetime.now()

    # Get activities organized by the user
    activities_you_host = Activity.objects.filter(
        activityOrganizer=user,
        activityDate__gte=current_time
    ).order_by('-activityCreateDate')

    # Get activities joined by the user
    activities_you_join = ActivityParticepationList.objects.filter(
        userId=user,
        activityId__activityDate__gte=current_time
    ).select_related('activityId').order_by('-activityId__activityCreateDate')

    # Get live posts for the user
    live_posts = Post.objects.filter(
        userId=user,
        postStatus='live'
    ).prefetch_related('image_set').order_by('-postDate')

    for post in live_posts:
        post.num_likes = post.like_set.count()
        post.num_comments = post.comment_set.count()
        post.num_saves = post.save_set.count()
        post.user_has_liked = post.like_set.filter(userId=request.user).exists()
        post.user_has_saved = post.save_set.filter(userId=request.user).exists()

    print(activities_you_join)

    context = {
        'user': user,
        'activities_you_host': activities_you_host,
        'activities_you_join': activities_you_join,
        'live_posts': live_posts,
    }

    return render(request, 'hello_public/user_dashboard.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import EditProfileForm

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        print(form)
        if form.is_valid():
            form.save()
            print(form)
            # messages.success(request, 'Your profile has been updated.')
            return redirect('hello_public:user_dashboard')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'hello_public/edit_profile.html', {'form': form})

from .forms import UpdatePasswordForm

def update_password(request):
    if request.method == 'POST':
        form = UpdatePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # messages.success(request, 'Your password has been updated.')
            return redirect('hello_public:user_dashboard')
    else:
        form = UpdatePasswordForm(request.user)
    return render(request, 'hello_public/update_password.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('hello_public:login')
    else:
        return render(request, 'hello_public/delete_account.html')

@login_required(login_url='hello_public:login')
def other_user_dashboard(request, user_id):
    user = get_object_or_404(User, id=user_id)
    posts = Post.objects.filter(userId=user).prefetch_related('image_set')
    hosted_activities = Activity.objects.filter(activityOrganizer=user)
    i_ignore_this_user = False
    i_ignore_this_user = IgnoreNotification.objects.filter(user=user, ignored_by=request.user).exists()
    
    for post in posts:
        post.num_likes = post.like_set.count()
        post.num_comments = post.comment_set.count()
        post.num_saves = post.save_set.count()
        post.user_has_liked = post.like_set.filter(userId=request.user).exists()
        post.user_has_saved = post.save_set.filter(userId=request.user).exists()

    if request.user.id == user_id:
        return redirect(reverse('hello_public:user_dashboard'))

    context = {
        'user': user,
        'posts': posts,
        'hosted_activities': hosted_activities,
        'ignore_this_user' : i_ignore_this_user
    }
    return render(request, 'hello_public/other_user_dashboard.html', context)

@login_required(login_url='hello_public:login')
def saved_posts(request):
    saved_posts = Save.objects.filter(userId=request.user).select_related('postId')
    post_ids = [save.postId_id for save in saved_posts]
    live_posts = Post.objects.filter(id__in=post_ids, postStatus='live').prefetch_related('image_set').select_related('userId').order_by('-postDate')

    for post in live_posts:
        post.num_likes = post.like_set.count()
        post.num_comments = post.comment_set.count()
        post.num_saves = post.save_set.count()
        post.user_has_liked = post.like_set.filter(userId=request.user).exists()
        post.user_has_saved = True

    context = {
        'live_posts': live_posts,
        'active_activities': None
    }

    return render(request, 'hello_public/user_save_post.html', context)

@login_required(login_url='hello_public:login')
def get_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(notificationReceiver=user).order_by('-notificationTime').select_related('notificationSender')
    notification_data = []
    has_unread_notification = False
    for notification in notifications:
        notification_time = timesince(notification.notificationTime)
        if 'minute' not in notification_time and 'hour' not in notification_time:
            notification_time = notification.notificationTime.strftime('%d %b %Y')
        notification_dict = {
            'notificationId': notification.id,
            'notificationTime': notification_time,
            'notificationLink': notification.notificationLink,
            'notificationType': notification.notificationType,
            'notificationOn': notification.notificationOn,
            'notificationStatus': notification.notificationStatus,
            'senderFullName': notification.notificationSender.get_full_name() if notification.notificationSender.get_full_name() else 'Null Null',
            'senderProfileImage': notification.notificationSender.profileImage.url if notification.notificationSender.profileImage else '/default_profile_image.png',
            'isOfficialUser': notification.notificationSender.userType == 'official' if notification.notificationSender else False
        }
        notification_data.append(notification_dict)
        if notification.notificationStatus == 'unread':
            has_unread_notification = True

    return JsonResponse({'notifications': notification_data, 'has_unread_notification': has_unread_notification})

@login_required(login_url='hello_public:login')
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, notificationReceiver=request.user)
    notification.notificationStatus = 'read'
    notification.save()
    return JsonResponse({'status': 'success'})

def error_404(request, exception):
    return render(request, 'hello_public/404page.html', status=404)

from django.shortcuts import get_object_or_404

def add_ignore(request, user_id):
    user = get_object_or_404(User, id=user_id)
    ignore_notification = IgnoreNotification.objects.create(user=user, ignored_by=request.user)
    ignore_notification.save()
    return JsonResponse({'success': True})

def remove_ignore(request, user_id):
    user = get_object_or_404(User, id=user_id)
    ignore_notification = IgnoreNotification.objects.filter(user=user, ignored_by=request.user).first()
    if ignore_notification:
        ignore_notification.delete()
    return JsonResponse({'success': True})

def get_notification_message(request, notification_id):
    message = Notification.objects.get(pk = notification_id)
    return render(request, 'hello_public/notification_message.html', {'message':message})

def create_report(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    moderators = User.objects.filter(userType = 'moderator')

    if request.method == 'POST':
        form = ReportPostForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.postId = post
            report.save()

            post.is_reported = True
            post.save()

            for user in moderators:
                create_notification(post_id, request.user, user, 'post', 'report')

            return redirect('hello_public:home')
    else:
        form = ReportPostForm()
    return render(request, 'hello_public/create_report.html', {'form': form, 'post': post})

@login_required(login_url='hello_public:login')
def moderator_delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST':
        comment.delete()

        why_delete = request.POST['why_delete']
        # send email to post owner
        subject = 'Comment delete'
        message = f"{why_delete} Deleted by moderator:{request.user.id}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [comment.userId.email]
        send_mail(subject, message, from_email, recipient_list)

        data = {'success': True}
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request method.'})

@login_required(login_url='hello_public:login')
def moderator_delete_reply(request, reply_id):
    comment = get_object_or_404(Reply, pk=reply_id)
    if request.method == 'POST':
        comment.delete()

        why_delete = request.POST['why_delete']
        # send email to post owner
        subject = 'Comment delete'
        message = f"{why_delete} Deleted by moderator:{request.user.id}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [comment.userId.email]
        send_mail(subject, message, from_email, recipient_list)

        data = {'success': True}
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request method.'})
    
def all_notification(request):
    notifications = Notification.objects.filter(notificationReceiver = request.user)
    return render(request, 'hello_public/all_notification.html', {'notifications': notifications})

from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Q
from .models import ActivityLocation

class ActivityLocationSuggestionsView(View):
    def get(self, request):
        query = request.GET.get('query', '')
        if len(query) < 2:
            # Return an empty list if the query is too short
            return JsonResponse({'suggestions': []})

        # Use a case-insensitive search to find matching locations
        matching_locations = ActivityLocation.objects.filter(Q(location_name__icontains=query))

        # Return a list of location names as suggestions
        suggestions = [location.location_name for location in matching_locations]

        return JsonResponse({'suggestions': suggestions})
