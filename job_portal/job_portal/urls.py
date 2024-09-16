"""
URL configuration for job_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from job.views import *
from django.conf import settings
from django.conf.urls.static import static


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',index,name='index'),
    path('user_signup/',user_signup,name='user_signup'),
    path('user_home/',user_home,name='user_home'),
    path('Logout/',Logout,name='Logout'),
    path('recruiter_signup/',recruiter_signup,name='recruiter_signup'),
    path('recruiter_home/',recruiter_home,name='recruiter_home'),
    path('view_users/',view_users,name='view_users'),
    path('delete_user/<int:pid>',delete_user,name='delete_user'),
    path('recruiter_pending/',recruiter_pending,name='recruiter_pending'),
    path('change_status/<int:pid>',change_status,name='change_status'),
    path('recruiter_accepted/',recruiter_accepted,name='recruiter_accepted'),
    path('recruiter_rejected/',recruiter_rejected,name='recruiter_rejected'),
    path('recruiter_all/',recruiter_all,name='recruiter_all'),
    path('delete_recruiter/<int:pid>',delete_recruiter,name='delete_recruiter'),
    path('change_password/', change_password, name='change_password'),
    path('job_add/', job_add, name='job_add'),
    path('job_list/', job_list, name='job_list'),
    path('job_edit/<int:pid>', job_edit, name='job_edit'),
    path('job_view/<int:pid>', job_view, name='job_view'),
    path('latest_jobs/', latest_jobs, name='latest_jobs'),
    path('user_latest_jobs/', user_latest_jobs, name='user_latest_jobs'),
    path('job_detail/<int:pid>', job_detail, name='job_detail'),
    path('apply_for_job/<int:pid>', apply_for_job, name='apply_for_job'),
    path('applied_candidates_list/', applied_candidates_list, name='applied_candidates_list'),
    path('login_view/', login_view, name='login_view'),
    path('job_search/', job_search, name='job_search'),
    path('user_profile/', user_profile, name='user_profile'),
    path('recruiter_profile/', recruiter_profile, name='recruiter_profile'),
    path('admin_profile/', admin_profile, name='admin_profile'),
    path('delete_job/<int:pid>', delete_job, name='delete_job'),
    path('change_application_status/<int:application_id>/<str:action>/', accept_or_reject_application, name='change_application_status'),
    path('applied_candidates_job/<int:job_id>', applied_candidates_job, name='applied_candidates_job'),
    path('login/', LoginAPI.as_view()),


    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('verify_otp/', verify_otp, name='verify_otp'),
    path('resend_verification_email/', resend_verification_email, name='resend_verification_email'),
    path('account_activation_success/', account_activation_success, name='account_activation_success'),

    path('api/user-profile/', UserProfileView.as_view(), name='user-profile'),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
