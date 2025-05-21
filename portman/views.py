from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
import logging
from ipaddress import ip_address
from PIL import Image

from .models import (
    Achievement, Certification, Education, Profile, Publication, WorkExperience, Skill, Project, ToolTechnology
)
from .forms import (
    EducatonForm, ProfileForm, UserRegistrationForm, WorkExperienceForm, SkillForm, CertificationForm,
    ProjectForm, AchievementForm, PublicationForm, ToolTechnologyForm
)

logger = logging.getLogger(__name__)

# --- Security: Rate Limiting ---
def rate_limit(request, key_prefix, limit=5, timeout=300):
    ip = request.META.get('REMOTE_ADDR')
    try:
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

# --- Helpers ---
def get_user_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile

def get_profile_picture(user):
    # If you use Django's media storage, adjust this as needed
    if user.profile.profile_picture:
        return user.profile.profile_picture.url
    return "/static/default-profile.png"

# --- Public Pages ---
def home(request):
    profiles = Profile.objects.select_related('user').filter(user__is_staff=False, user__is_superuser=False)
    return render(request, 'index.html', {'profiles': profiles})

def user_details(request, user_id):
    profile = get_object_or_404(Profile, pk=user_id)
    return render(request, 'dashboard.html', {'profile': profile})

# --- Authentication ---
User = get_user_model()

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid login credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

def forget_password(request):
    return render(request, 'forget_pass.html')

# --- Registration ---
@csrf_protect
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect('register')
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "Account created successfully. Complete your profile.")
            return redirect('edit_profile')
        else:
            messages.error(request, "Invalid form data.")
            return redirect('register')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

# --- Dashboard ---
@login_required
@csrf_protect
def dashboard(request):
    profile = get_user_profile(request.user)
    return render(request, 'dashboard.html', {'profile': profile})

# --- Profile Editing ---
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif']
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

def is_valid_image(file):
    try:
        file.seek(0)
        img = Image.open(file)
        img.verify()
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
            full_name = request.POST.get('full_name')
            if full_name:
                name_parts = full_name.split()
                request.user.first_name = name_parts[0]
                request.user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                request.user.save()
            if request.FILES.get('profile_picture'):
                file = request.FILES['profile_picture']
                if not (is_valid_image(file) and file.size <= MAX_FILE_SIZE):
                    messages.error(request, "Invalid image file.")
            messages.success(request, 'Profile updated!')
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

# --- Contact Info ---
@login_required
@csrf_protect
@require_http_methods(["POST"])
def edit_contact_info(request):
    profile = get_user_profile(request.user)
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

# --- Education ---
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
        messages.success(request, "Education added successfully!")
    else:
        messages.error(request, f"Error adding education: {form.errors}")
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
        messages.success(request, "Work experience added successfully!")
    else:
        messages.error(request, f"Error adding work experience: {form.errors}")
    return redirect('dashboard')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def edit_work_experience(request, pk):
    profile = get_user_profile(request.user)
    experience = get_object_or_404(WorkExperience, pk=pk, profile=profile)
    form = WorkExperienceForm(request.POST, instance=experience)
    if form.is_valid():
        form.save()
        messages.success(request, "Work experience updated!")
    else:
        messages.error(request, f"Error updating work experience: {form.errors}")
    return redirect('dashboard')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_work_experience(request, pk):
    profile = get_user_profile(request.user)
    experience = get_object_or_404(WorkExperience, pk=pk, profile=profile)
    experience.delete()
    messages.success(request, "Work experience deleted!")
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
        messages.success(request, "Project added successfully!")
    else:
        messages.error(request, f"Error adding project: {form.errors}")
    return redirect('dashboard')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.profile.user != request.user:
        messages.error(request, "You are not authorized to delete this project.")
        return redirect('dashboard')
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
        messages.success(request, "Skill added successfully!")
    else:
        messages.error(request, f"Error adding skill: {form.errors}")
    return redirect('dashboard')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_skill(request, pk):
    profile = get_user_profile(request.user)
    skill = get_object_or_404(Skill, pk=pk, profile=profile)
    skill.delete()
    messages.success(request, "Skill deleted!")
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
        messages.success(request, "Technology added successfully!")
    else:
        messages.error(request, f"Error adding technology: {form.errors}")
    return redirect('dashboard')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_technology(request, pk):
    profile = get_user_profile(request.user)
    technology = get_object_or_404(ToolTechnology, pk=pk, profile=profile)
    technology.delete()
    messages.success(request, "Technology deleted!")
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
        messages.success(request, "Certification added successfully!")
    else:
        messages.error(request, f"Error adding certification: {form.errors}")
    return redirect('dashboard')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_certification(request, pk):
    profile = get_user_profile(request.user)
    certification = get_object_or_404(Certification, pk=pk, profile=profile)
    certification.delete()
    messages.success(request, "Certification deleted!")
    return redirect('dashboard')

# --- Gallery ---
@login_required
@csrf_protect
@require_http_methods(["POST"])
def add_gallery_image(request):
    profile = get_user_profile(request.user)
    if request.FILES.get('gallery_image'):
        image = request.FILES['gallery_image']
        caption = request.POST.get('caption', '')
        project_id = request.POST.get('project')
        # Save the image to the media directory (implement as needed)
        messages.success(request, "Gallery image added successfully!")
    else:
        messages.error(request, "No image uploaded.")
    return redirect('dashboard')

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
        messages.success(request, "Publication added successfully!")
    else:
        messages.error(request, f"Error adding publication: {form.errors}")
    return redirect('dashboard')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_publication(request, pk):
    profile = get_user_profile(request.user)
    publication = get_object_or_404(Publication, pk=pk, profile=profile)
    publication.delete()
    messages.success(request, "Publication deleted!")
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
        messages.success(request, "Achievement added successfully!")
    else:
        messages.error(request, f"Error adding achievement: {form.errors}")
    return redirect('dashboard')

@login_required
@csrf_protect
@require_http_methods(["POST"])
def delete_achievement(request, pk):
    profile = get_user_profile(request.user)
    achievement = get_object_or_404(Achievement, pk=pk, profile=profile)
    achievement.delete()
    messages.success(request, "Achievement deleted!")
    return redirect('dashboard')

# --- PDF Export ---
@login_required
def export_resume_pdf(request):
    # This is handled client-side with html2pdf.js
    return redirect('dashboard')