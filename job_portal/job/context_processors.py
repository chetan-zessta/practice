# using context processors 
from .models import StudentUser, Recruiter, Job

def common_context(request):
    user_type = None
    latest_jobs = Job.objects.order_by('-start_date')[:9]
    if request.user.is_authenticated:
        if request.user.is_staff:
            user_type = 'admin'
        else:
            try:
                student_user = StudentUser.objects.get(user=request.user)
                user_type = student_user.type
            except StudentUser.DoesNotExist:
                try:
                    recruiter = Recruiter.objects.get(user=request.user)
                    user_type = recruiter.type
                except Recruiter.DoesNotExist:
                    user_type = "None"
    return {
        'user_type': user_type,
        'latest_jobs': latest_jobs
    }
