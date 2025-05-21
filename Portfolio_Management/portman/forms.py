from django import forms
from .models import (Education, Profile, WorkExperience, Skill, Certification, Project, Achievement, Endorsement, Publication, ToolTechnology)
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

# --- User Dashboard ---

from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name'})
    )

    class Meta:
        model = Profile
        fields = [
            'bio', 'profile_picture', 
            'phone_number', 'location', 'github', 'linkedin', 'website'
        ]
        widgets = {
            
            'bio': forms.Textarea(attrs={'placeholder': 'Tell us about yourself...', 'rows': 4}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+1 (123) 456-7890'}),
            'location': forms.TextInput(attrs={'placeholder': 'City, Country'}),
            'github': forms.URLInput(attrs={'placeholder': 'https://github.com/username'}),
            'linkedin': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/username'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourportfolio.com'}),
        }

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if full_name:
            # Optional: Add any specific validation for full name
            return full_name
        return None

# --- Registration Form ---
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  # Correct fields




# ---Contact Info---
class ContactInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True)  # Add this for email support

    class Meta:
        model = Profile
        fields = ['phone_number', 'location']

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.email = self.cleaned_data['email']  # Update email
        if commit:
            profile.user.save()
            profile.save()
        return profile


# ---User Login---
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))

# ---Password Storing---
class PasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password']
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'form-input'}),
        }
    pass


# ---Project's Form ---
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'tools_used', 'start_date', 'end_date', 'repository_url','live_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'tools_used': forms.TextInput(attrs={'class': 'form-input'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'repository_url': forms.URLInput(attrs={'class': 'form-input'}),
            'live_url': forms.URLInput(attrs={'class': 'form-input'}),
        }

class EducatonForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['school_name', 'degree', 'start_date', 'end_date', 'description']
        widgets ={
            'school_name': forms.TextInput(attrs={'class': 'form-input'}),
            'degree': forms.TextInput(attrs={'class': 'form-input'}),
            'start_date' : forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date' : forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'description' : forms.Textarea(attrs={'rows': 3, 'class': 'form-input'})
        }

class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ['company_name', 'position', 'start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'level']
        widgets = {
            'level': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
        }

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['title', 'organization', 'issue_date', 'expiration_date', 'credential_url']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'credential_url': forms.URLInput(attrs={'class': 'form-input'}),
        }

class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
        }

class EndorsementForm(forms.ModelForm):
    class Meta:
        model = Endorsement
        fields = ['endorsed_by', 'skill', 'message']
        widgets = {
            'endorsed_by': forms.TextInput(attrs={'class': 'form-input'}),
            'skill': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
        }

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['title', 'description', 'publication_date', 'link']
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-input'}),
            'link': forms.URLInput(attrs={'class': 'form-input'}),
        }

class ToolTechnologyForm(forms.ModelForm):
    class Meta:
        model = ToolTechnology
        fields = ['name', 'category']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
        }

