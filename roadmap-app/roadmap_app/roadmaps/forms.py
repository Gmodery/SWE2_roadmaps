from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import AppUser, Class, Roadmap, Project

# ------------------------------
# STUDENT / INSTRUCTOR SIGNUP FORM
# ------------------------------
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

# ------------------------------
# ADMIN: CREATE DJANGO USER (for AppUser pairing)
# ------------------------------
class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()

# ------------------------------
# ADMIN: ASSIGN ROLE TO USER
# ------------------------------
class AppUserRoleForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ['role']

# ------------------------------
# INSTRUCTOR: CREATE CLASS FORM
# ------------------------------
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

# ------------------------------
# INSTRUCTOR: CREATE PROJECT FORM
# ------------------------------
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
