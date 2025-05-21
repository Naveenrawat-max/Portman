from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    
    path('', views.home, name='home'),
    
    # path('portfolio/<str:username>/', views.portfolio_detail, name='portfolio_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/edit-profile/', views.edit_profile, name='edit_profile'),
    path('dashboard/add-work-experience/', views.add_work_experience, name='add_work_experience'),
    path('dashboard/edit-work-experience/<int:pk>/', views.edit_work_experience, name='edit_work_experience'),
    path('dashboard/delete-work-experience/<int:pk>/', views.delete_work_experience, name='delete_work_experience'),
    path('dashboard/add-project/', views.add_project, name='add_project'),
    path('dashboard/delete-project/<int:project_id>/', views.delete_project, name='delete_project'),
    # path('dashboard/edit-project/', views.edit_project, name='edit_project'),
    path('dashboard/add-education/', views.add_education, name='add_education'),
    # path('dashboard/edit-education/', views.edit_education, name='edit_education'),
    # path('dashboard/delete-education/', views.delete_education, name='delete_education'),
    path('dashboard/add-skill/', views.add_skill, name='add_skill'),
    # path('dashboard/edit-skill/', views.edit_skill, name='edit_skill'),
    path('dashboard/delete-skill/<int:pk>/', views.delete_skill, name='delete_skill'),
    
    # New URL patterns for the added features
    path('dashboard/add-technology/', views.add_technology, name='add_technology'),
    path('dashboard/delete-technology/<int:pk>/', views.delete_technology, name='delete_technology'),
    path('dashboard/add-certification/', views.add_certification, name='add_certification'),
    path('dashboard/delete-certification/<int:pk>/', views.delete_certification, name='delete_certification'),
    path('dashboard/add-publication/', views.add_publication, name='add_publication'),
    path('dashboard/delete-publication/<int:pk>/', views.delete_publication, name='delete_publication'),
    path('dashboard/add-gallery-image/', views.add_gallery_image, name='add_gallery_image'),
    path('dashboard/export-resume-pdf/', views.export_resume_pdf, name='export_resume_pdf'),
    
    path('dashboard/edit-contact-info/', views.edit_contact_info, name='edit_contact_info'),
    path('user/<int:user_id>/', views.user_details, name='user_details'),   
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path('login/forget_password/', auth_views.PasswordResetView.as_view(), name='forget_password'),
]
