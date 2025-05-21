from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    appwrite_user_id = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, help_text="Brief description about yourself")
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class WorkExperience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="work_experiences")
    company_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.position} at {self.company_name}"


class Skill(models.Model):
    name = models.CharField(max_length=100)
    level = models.CharField(
        max_length=50,
        choices=[
            ('Beginner', 'Beginner'),
            ('Intermediate', 'Intermediate'),
            ('Advanced', 'Advanced'),
            ('Expert', 'Expert'),
        ]
    )
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="skills")

    def __str__(self):
        return f"{self.name} ({self.level})"

# Education model to store educational background
class Education(models.Model):
    user_profile = models.ForeignKey(Profile, related_name='education', on_delete=models.CASCADE)
    school_name = models.CharField(max_length=200)
    degree = models.CharField(max_length=100)
    start_date = models.PositiveIntegerField()
    end_date = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.degree} at {self.school_name}"


class Certification(models.Model):
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    issue_date = models.DateField()
    expiration_date = models.DateField(blank=True, null=True)
    credential_url = models.URLField(blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="certifications")

    def __str__(self):
        return f"{self.title} by {self.organization}"


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tools_used = models.TextField(help_text="Comma-separated list of tools/technologies")
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    live_url= models.URLField(blank=True, null=True, help_text="Link to the live version of the project")
    repository_url = models.URLField(blank=True, null=True, help_text="Link to the project's source code")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="projects")

    def __str__(self):
        return self.title


class Achievement(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="achievements")

    def __str__(self):
        return self.title


class Endorsement(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="endorsements")
    endorsed_by = models.CharField(max_length=255, help_text="Name of the person/organization endorsing you")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="endorsements")
    message = models.TextField(blank=True, help_text="Optional message from the endorser")

    def __str__(self):
        return f"Endorsement by {self.endorsed_by} for {self.skill.name}"


class Publication(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="publications")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text="Brief description of the publication")
    publication_date = models.DateField()
    link = models.URLField(blank=True, null=True, help_text="Link to the publication (if available)")

    def __str__(self):
        return self.title


class ToolTechnology(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=[
            ('Programming Language', 'Programming Language'),
            ('Framework', 'Framework'),
            ('Tool', 'Tool'),
            ('Other', 'Other'),
        ]
    )
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="tools")

    def __str__(self):
        return f"{self.name} ({self.category})"
