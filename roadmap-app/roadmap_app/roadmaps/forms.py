from django import forms
from .models import AppUser, Class, Roadmap, Project
from django.contrib.auth.forms import UserCreationForm

# forms.py handles form validation and structure and can be called
# from an html file so we don't have to manually make the forms in there

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = AppUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role']

class CreateClassForm(forms.ModelForm):
    class_name = forms.CharField(max_length=30, required=True)
    class_desc = forms.CharField(max_length=160, required=True)

    class Meta:
        model = Class
        fields = ["class_name", "class_desc"]


class CreateProjectForm(forms.ModelForm):
    project_name = forms.CharField(max_length=30, required=True)
    project_desc = forms.CharField(max_length=160, required=True)

    class Meta:
        model = Project
        fields = ["project_name", "project_description"]
