from django import forms
from .models import AppUser, Class, Roadmap, Project
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter First Name'})
    )
    last_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter Email'})
    )
    username = forms.CharField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Username'})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = AppUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role']

class CreateClassForm(forms.ModelForm):
    class_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Class Name'})
    )
    class_desc = forms.CharField(
        max_length=160, required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Class Description', 'rows': 3})
    )

    class Meta:
        model = Class
        fields = ["class_name", "class_desc"]

class CreateProjectForm(forms.ModelForm):
    project_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Project Name'})
    )
    project_desc = forms.CharField(
        max_length=160, required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Project Description', 'rows': 3})
    )

    class Meta:
        model = Project
        fields = ["project_name", "project_desc"]
