from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Profile, WorkExperience, Skill, Certification, Project, 
    Achievement, Endorsement, Publication, ToolTechnology,Education
)

# Inline editing for related models

# Profile Inline admin allows editing of the Profile model within the User admin page
class ProfileInline(admin.StackedInline):
    model = Profile  # Model to inline
    can_delete = False  # Prevent deletion from inline view
    verbose_name_plural = "Profile"  # Plural name for the inline

# Skill Inline admin allows editing of the Skill model within the User admin page
class SkillInline(admin.StackedInline):
    model = Skill  # Model to inline
    extra = 1  # Display 2 empty rows for adding new skills

class CertificationInline(admin.StackedInline):
    model= Certification
    extra=1


# Register your models here
# Education Inline admin allows editing of Education records within the User admin page
class EducationInline(admin.StackedInline):
    model = Education  # Model to inline
    extra = 1  # Display 1 extra row for adding new education entries
    verbose_name_plural = "Education"  # Plural name for the inline

# Work Experience Inline admin allows editing of WorkExperience records within the User admin page
class WorkExperienceInline(admin.StackedInline):    
    model = WorkExperience  # Model to inline
    extra = 1  # Display 1 extra row for adding new work experience entries
    verbose_name_plural = "Work Experience"  # Plural name for the inline

# Project Inline admin allows editing of Project records within the User admin page
class ProjectInline(admin.StackedInline):
    model = Project  # Model to inline
    extra = 1  # Display 1 extra row for adding new projects
    verbose_name_plural = "Projects"  # Plural name for the inline

class CustomUserAdmin(UserAdmin):  # Extend UserAdmin properly
    inlines = (ProfileInline,)
    list_display = UserAdmin.list_display + ('email', 'first_name', 'last_name')  # Example customization
    list_filter = UserAdmin.list_filter + ('is_staff', 'is_superuser')  # Example customization
    search_fields = UserAdmin.search_fields + ('email',)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'website', 'linkedin', 'github')
    search_fields = ('user__username', 'bio')
    inlines = [WorkExperienceInline, SkillInline, CertificationInline, ProjectInline, EducationInline]


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('position', 'company_name', 'start_date', 'end_date', 'profile')
    search_fields = ('company_name', 'position', 'profile__user__username')
    list_filter = ('start_date', 'end_date')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'profile')
    search_fields = ('name', 'profile__user__username')
    list_filter = ('level',)

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'degree', 'start_date', 'end_date', 'user_profile')
    search_fields = ('school_name', 'degree', 'profile__user__username')
    list_filter = ('start_date', 'end_date')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'issue_date', 'expiration_date', 'profile')
    search_fields = ('title', 'organization', 'profile__user__username')
    list_filter = ('organization', 'issue_date')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'profile')
    search_fields = ('title', 'tools_used', 'profile__user__username')
    list_filter = ('start_date', 'end_date')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'profile')
    search_fields = ('title', 'profile__user__username')
    list_filter = ('date',)

@admin.register(Endorsement)
class EndorsementAdmin(admin.ModelAdmin):
    list_display = ('endorsed_by', 'skill', 'profile')
    search_fields = ('endorsed_by', 'skill__name', 'profile__user__username')

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'publication_date', 'profile')
    search_fields = ('title', 'profile__user__username')
    list_filter = ('publication_date',)

@admin.register(ToolTechnology)
class ToolTechnologyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'profile')
    search_fields = ('name', 'category', 'profile__user__username')
    list_filter = ('category',)
