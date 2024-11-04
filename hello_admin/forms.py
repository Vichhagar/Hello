from django import forms
from django.contrib.auth.forms import UserChangeForm
from hello_public.models import User
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User

class UpdateUserRoleForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['userType']
        labels = {
            'userType': 'New User Role',
        }
        widgets = {
            'userType': forms.Select(choices=User.USER_TYPE),
        }


class UpdatePasswordForm(PasswordChangeForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your new password'}),
        label='New Password'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your new password'}),
        label='Confirm Password'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('old_password')

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profileImage', 'first_name', 'last_name', 'userBio', 'username']
        labels = {'profileImage': 'Profile Image', 'userBio': 'Bio', 'username': 'username'}
        widgets = {'userBio': forms.Textarea(attrs={'rows': 3})}

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1", 
            "password2",
            "userType"
        ]
        widgets = {
            'userType': forms.Select(choices=User.USER_TYPE),
        }
