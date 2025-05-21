from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.http import HttpResponse
import os
from django.conf import settings
import json

from ipaddress import ip_address
import logging
from django.core.cache import cache

from .models import (
    Achievement, Certification, Education, Profile, Publication, WorkExperience, Skill, Project, ToolTechnology
)
from .forms import (
    EducatonForm, ProfileForm, UserRegistrationForm, WorkExperienceForm, SkillForm, CertificationForm,
    ProjectForm, AchievementForm, PublicationForm, ToolTechnologyForm
)
from PIL import Image

from .appwrite_sync import sync_to_appwrite, upload_file_to_appwrite, get_public_file_url
from .appwrite_sync import sync_to_appwrite
from .appwrite_config import client
from appwrite.client import Client
from appwrite.id import ID
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage


# Initialize Appwrite client
client = Client()
client.set_endpoint("https://cloud.appwrite.io/v1")  # Replace with your endpoint
client.set_project("67d090e90034dde1e899")          # Replace with your project ID
client.set_key("standard_13e1b9551affac5b1a4aa60e285409d819eea8e39f0992b02d0eb184c8e1513f3f1422e3b633406e0a5d08a3624b0e81e11a953da293854203f0f633056554225cb36cb3f07c3c16e4b782d2e97c6ede19cbe17dfcea6cb959d628c77fb6ede33870d645c0ab7b2cd95711ae12b23163f2c7fb73e4cad1b668d1973646734f13")             # Replace with your API key

account = Account(client)
account = Account(client)
databases = Databases(client)
appwrite_account = Account(client)
appwrite_db = Databases(client)
DATABASE_ID = "67d09163002ea9ef0c8b"
PROFILE_COLLECTION_ID = "67e18ac60031f956b070"


# Helper to fetch Profile
def get_user_profile(user):
    user = Profile.objects.exclude(user__is_superuser=True)
    return get_object_or_404(Profile, user=user)

def get_profile_picture(user):
    storage = Storage(client)
    try:
        return storage.get_file_view("67d1babc00201ad80d75", user.profile.profile_picture)
    except Exception:
        return "/static/default-profile.png"  # Fallback in case of error


# --- Public Pages ---
def home(request):
    """Display all users' profiles in card format."""
    profiles = Profile.objects.select_related('user').filter(user__is_staff=False, user__is_superuser=False)
    return render(request, 'index.html', {'profiles': profiles})

# Security Logging
logger = logging.getLogger(__name__)
def rate_limit(request, key_prefix, limit=5, timeout=300):
    """
    Implement rate limiting for sensitive operations
    """
    ip = request.META.get('REMOTE_ADDR')
    try:
        # Validate IP address
        ip_address(ip)
    except ValueError:
        logger.warning(f"Invalid IP address: {ip}")
        return False

    cache_key = f'{key_prefix}_{ip}'
    attempts = cache.get(cache_key, 0)
    
    if attempts >= limit:
        logger.warning(f"Rate limit exceeded for {ip}")
        return False
    
    cache.set(cache_key, attempts + 1, timeout)
    return True


#-------user Portfolio-----------
def user_details(request, user_id):
    """
    Display details for a specific user profile.
    """
    # Fetch the Profile object by ID
    
    profile = get_object_or_404(Profile, pk=user_id)

    return render(request, 'dashboard.html', {
        'profile': profile,
    })

    
    
#---------Login-------------
def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            account = Account(client)
            try:
                session = account.create_email_session(email, password)
                request.session['appwrite_session'] = session['$id']  # Store session ID
                messages.success(request, "Login successful!")
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, "Invalid login credentials.")
    
    return render(request, 'login.html', {'form': AuthenticationForm()})


#-------Logout----------
def logout_view(request):
    if 'appwrite_session' in request.session:
        account = Account(client)
        try:
            account.delete_session(request.session['appwrite_session'])
            del request.session['appwrite_session']
        except Exception:
            messages.error(request, "Error logging out.")

    logout(request)
    return redirect('login')  # Redirect to login page after logout



#--------Forget Password-------
def forget_password(request):
    return render(request, 'forget_pass.html')

#-----Register-------
User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            # Prevent duplicate Django usernames
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect('register')

            try:
                # Initialize Appwrite Account Service
                account = Account(client)

                # Create user in Appwrite (primary user storage)
                appwrite_user = account.create(user_id="unique()", email=email, password=password)

                # (Optional) Create a local Django user for now
                django_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                # Create Profile while avoiding UNIQUE constraint error
                Profile.objects.get_or_create(
                    user=django_user,
                    defaults={'appwrite_user_id': appwrite_user['$id']}
                )

                # Auto-login the Django user
                login(request, django_user)
                messages.success(request, "Account created successfully. Complete your profile.")
                return redirect('edit_profile')

            except Exception as e:
                messages.error(request, f"Appwrite Error: {str(e)}")
                return redirect('register')

        else:
            messages.error(request, "Invalid form data.")
            return redirect('register')

    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


# --- User Dashboard ---

@login_required
@csrf_protect
def dashboard(request):
    """Display the logged-in user's dashboard."""
    profile = get_user_profile(request.user)
    return render(request, 'dashboard.html', {'profile': profile})


# --- Profile Editing ---


# Constants for validation
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif']
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

def is_valid_image(file):
    try:
        file.seek(0)
        img = Image.what(file)
        img.verify()  # Reset the file pointer
        return img.format.lower() in ['jpeg', 'png', 'gif']
    except Exception:
        return False

@login_required
@csrf_protect
def edit_profile(request):
    profile = get_user_profile(request.user)
    work_experience_form = WorkExperienceForm()

    if request.method == 'POST':
        if 'add_work_experience' in request.POST:
            work_experience_form = WorkExperienceForm(request.POST)
            if work_experience_form.is_valid():
                work_experience = work_experience_form.save(commit=False)
                work_experience.profile = profile
                work_experience.save()
                messages.success(request, 'Work experience added successfully!')
                return redirect('edit_profile')

        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save()

            # Update Django user's name
            full_name = request.POST.get('full_name')
            if full_name:
                name_parts = full_name.split()
                request.user.first_name = name_parts[0]
                request.user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                request.user.save()

            # Upload image to Appwrite if changed
            appwrite_image_url = ""
            if request.FILES.get('profile_picture'):
                file = request.FILES['profile_picture']
                file_id = upload_file_to_appwrite(file)
                if file_id:
                    appwrite_image_url = get_public_file_url(file_id)

            # Sync all profile fields to Appwrite
            sync_to_appwrite(
                collection_id="67e18ac60031f956b070",  # profiles
                data={
                    "user_id": profile.user.id,
                    "bio": profile.bio,
                    "location": profile.location,
                    "phone_number": profile.phone_number,
                    "profile_picture": appwrite_image_url or str(profile.profile_picture.url if profile.profile_picture else "")
                }
            )

            messages.success(request, 'Profile updated and synced to Appwrite!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile)

    work_experiences = profile.work_experiences.all()

    return render(request, 'edit_profile.html', {
        'form': form,
        'profile': profile,
        'work_experience_form': work_experience_form,
        'work_experiences': work_experiences
    })





# --- Contact Information ---
@login_required
@csrf_protect
@require_http_methods(["POST"])
def edit_contact_info(request):
    if request.method == 'POST':
        profile = request.user.profile
        
        # Only update fields that are not empty
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        location = request.POST.get('location')
        
        if email:
            request.user.email = email
            request.user.save()
        
        if phone_number:
            profile.phone_number = phone_number
        
        if location:
            profile.location = location
        
        profile.save()
        
        messages.success(request, 'Contact information updated successfully!')
        return redirect('dashboard')
    
    return redirect('dashboard')

#---Education-----
@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_education(request):
    profile = get_user_profile(request.user)
    form = EducatonForm(request.POST)
    if form.is_valid():
        edu = form.save(commit=False)
        edu.profile = profile
        edu.save()

        sync_to_appwrite(
            collection_id="education",
            data={
                "user_id": profile.user.id,
                "school_name": edu.school_name,
                "degree": edu.degree,
                "start_year": edu.start_year,
                "end_year": edu.end_year,
                "description": edu.description
            }
        )
    return redirect('dashboard')

# --- Work Experience ---
@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_work_experience(request):
    profile = get_user_profile(request.user)
    form = WorkExperienceForm(request.POST)
    if form.is_valid():
        exp = form.save(commit=False)
        exp.profile = profile
        exp.save()

        sync_to_appwrite(
            collection_id="work_experience",
            data={
                "user_id": profile.user.id,
                "company_name": exp.company_name,
                "position": exp.position,
                "start_date": str(exp.start_date) if exp.start_date else None,
                "end_date": str(exp.end_date) if exp.end_date else None,
                "description": exp.description,
            }
        )
    return redirect('dashboard')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def edit_work_experience(request, pk):
    """Edit an existing work experience entry."""
    profile = get_user_profile(request.user)
    experience = get_object_or_404(WorkExperience, pk=pk, profile=profile)
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = WorkExperienceForm(instance=experience)
    return redirect('home')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_work_experience(request, pk):
    """Delete a work experience entry."""
    profile = get_user_profile(request.user)
    experience = get_object_or_404(WorkExperience, pk=pk, profile=profile)
    experience.delete()
    return redirect('dashboard')

# --- Projects ---
@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_project(request):
    profile = get_user_profile(request.user)
    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save(commit=False)
        project.profile = profile
        project.save()

        sync_to_appwrite(
            collection_id="projects",
            data={
                "user_id": profile.user.id,
                "title": project.title,
                "description": project.description,
                "tools_used": project.tools_used,
                "repository_url": project.repository_url,
                "live_url": project.live_url,
                "start_date": str(project.start_date) if project.start_date else None,
                "end_date": str(project.end_date) if project.end_date else None,
            }
        )
    return redirect('dashboard')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_project(request, project_id):
    """Delete a project."""
    project = get_object_or_404(Project, id=project_id)
    
    # Optional: Ensure only the owner can delete
    if project.profile.user != request.user:
        messages.error(request, "You are not authorized to delete this project.")
        return redirect('profile', profile_id=project.profile.id)
    
    project.delete()
    messages.success(request, "Project deleted successfully!")
    return redirect('dashboard')

# --- Skills ---
@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_skill(request):
    profile = get_user_profile(request.user)
    form = SkillForm(request.POST)
    if form.is_valid():
        skill = form.save(commit=False)
        skill.profile = profile
        skill.save()

        sync_to_appwrite(
            collection_id="skills",
            data={
                "user_id": profile.user.id,
                "name": skill.name,
                "level": skill.level,
            }
        )
    return redirect('dashboard')


@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_skill(request, pk):
    profile = get_user_profile(request.user)
    skill = get_object_or_404(Skill, pk=pk, profile=profile)
    skill.delete()
    return redirect('dashboard')

# --- Technologies ---
@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_technology(request):
    profile = get_user_profile(request.user)
    form = ToolTechnologyForm(request.POST)
    if form.is_valid():
        tech = form.save(commit=False)
        tech.profile = profile
        tech.save()

        sync_to_appwrite(
            collection_id="tools",
            data={
                "user_id": profile.user.id,
                "name": tech.name,
                "description": tech.description,
            }
        )
    return redirect('dashboard')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_technology(request, pk):
    profile = get_user_profile(request.user)
    technology = get_object_or_404(ToolTechnology, pk=pk, profile=profile)
    technology.delete()
    return redirect('dashboard')

# --- Certifications ---

@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_certification(request):
    profile = get_user_profile(request.user)
    form = CertificationForm(request.POST)
    if form.is_valid():
        certification = form.save(commit=False)
        certification.profile = profile
        certification.save()

        sync_to_appwrite(
            collection_id="certifications",
            data={
                "user_id": profile.user.id,
                "title": certification.title,
                "issuer": certification.issuer,
                "date_issued": str(certification.date_issued) if certification.date_issued else None,
            }
        )
    return redirect('dashboard')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_certification(request, pk):
    profile = get_user_profile(request.user)
    certification = get_object_or_404(Certification, pk=pk, profile=profile)
    certification.delete()
    return redirect('dashboard')

# --- Gallery ---
@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_gallery_image(request):
    profile = get_user_profile(request.user)
    if request.method == 'POST' and request.FILES.get('gallery_image'):
        image = request.FILES['gallery_image']
        caption = request.POST.get('caption', '')
        project_id = request.POST.get('project')
        
        # Save the image to the media directory
        # Implementation depends on your storage setup
        
        messages.success(request, "Gallery image added successfully!")
        return redirect('dashboard')
    
    return redirect('dashboard')

#---Other Sections-------

# --- Publications ---
@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_publication(request):
    profile = get_user_profile(request.user)
    form = PublicationForm(request.POST)
    if form.is_valid():
        pub = form.save(commit=False)
        pub.profile = profile
        pub.save()

        sync_to_appwrite(
            collection_id="publications",
            data={
                "user_id": profile.user.id,
                "title": pub.title,
                "journal": pub.journal,
                "publication_date": str(pub.publication_date) if pub.publication_date else None,
            }
        )
    return redirect('dashboard')


@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_publication(request, pk):
    profile = get_user_profile(request.user)
    publication = get_object_or_404(Publication, pk=pk, profile=profile)
    publication.delete()
    return redirect('dashboard')


# --- Achievements ---
@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_achievement(request):
    profile = get_user_profile(request.user)
    form = AchievementForm(request.POST)
    if form.is_valid():
        ach = form.save(commit=False)
        ach.profile = profile
        ach.save()

        sync_to_appwrite(
            collection_id="achievements",
            data={
                "user_id": profile.user.id,
                "title": ach.title,
                "description": ach.description,
                "date": str(ach.date) if ach.date else None,
            }
        )
    return redirect('dashboard')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_achievement(request, pk):
    profile = get_user_profile(request.user)
    achievement = get_object_or_404(Achievement, pk=pk, profile=profile)
    achievement.delete()
    return redirect('dashboard')

# --- PDF Export ---
@login_required
def export_resume_pdf(request):
    profile = get_user_profile(request.user)
    # This is handled client-side with html2pdf.js
    return redirect('dashboard')
