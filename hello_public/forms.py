from django import forms
from django.forms import inlineformset_factory
from .models import *
from django.contrib.auth.forms import UserCreationForm

# class JoinActivityForm(forms.ModelForm):
#     class Meta:
#         model = ActivityParticepationList
#         fields = (
#             'userID',
#             'activityID'
#         )

# class CreateActivityForm(forms.ModelForm):
#     class Meta:
#         model = Activity
#         fields = (
#             '__all__'
#         )

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username", 
            "first_name", 
            "last_name", 
            "password1", 
            "password2",
            "profileImage",
            "userType"
        ]

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['postText']

class ImageForm(forms.ModelForm):
    # remove = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    class Meta:
        model = Image
        fields = ['imageLink']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['commmentText']
        widgets = {
            'commmentText': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'commmentText': '',
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['replyText']

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['activityTitle', 'activityLocation', 'activityDiscription', 'activityDate', 'activityOpenDate', 'activityCloseDate']
        widgets = {
            'activityDate': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'activityOpenDate': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'activityCloseDate': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

from django import forms
from django.contrib.auth.forms import PasswordChangeForm

class UpdatePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your current password'}),
        label='Current Password'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your new password'}),
        label='New Password'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your new password'}),
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profileImage', 'first_name', 'last_name', 'userBio', 'username']
        labels = {'profileImage': 'Profile Image', 'userBio': 'Bio', 'username': 'username'}
        widgets = {'userBio': forms.Textarea(attrs={'rows': 3})}

class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['postText', 'postStatus', 'postType']
        widgets = {
            'postText': forms.Textarea(attrs={'rows': 5}),
        }

class ReportPostForm(forms.ModelForm):
    class Meta:
        model = ReportPost
        fields = ['Reason']

