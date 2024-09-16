from django.shortcuts import render,redirect, get_object_or_404
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from datetime import date
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.
def index(request):
    # Fetch latest jobs based on start_date
    user_type = None
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
    jobs = Job.objects.order_by('-start_date')[:9]
    d = {'jobs': jobs,'user_type': user_type}
    return render (request,'index.html',d)

from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(refresh.access_token)

from rest_framework_simplejwt.tokens import AccessToken

def login_with_token(request):
    if request.method == 'POST':
        # Assuming the access token is provided in the request POST data
        access_token = request.POST.get('access_token')
        if access_token:
            try:
                # Decode the access token to get the user
                token = AccessToken(access_token)
                user = token.payload.get('user_id')  # Assuming 'user_id' is present in the payload
                user_type = token.payload.get('user_type')  # Assuming 'user_type' is present in the payload
                # Check user type and redirect to respective profile
                if user_type == 'admin':
                    # Assuming 'admin_profile' is the URL name for admin profile
                    return redirect('admin_profile')
                elif user_type == 'student':
                    # Assuming 'user_profile' is the URL name for student profile
                    return redirect('user_profile')
                elif user_type == 'recruiter':
                    # Assuming 'job_list' is the URL name for job list page
                    return redirect('job_list')
            except Exception as e:
                # Handle token decoding errors or invalid tokens
                print("Token decoding error:", e)
    # If access token is missing or invalid, redirect to login page or show error message
    return redirect('login_page')

def login_view(request):

    if request.user.is_authenticated:
        # If the user is already logged in, redirect to their respective page
        if request.user.is_staff:
            return redirect('admin_profile')
        try:
            student = StudentUser.objects.get(user=request.user)
            if student.type == "user" and student.is_verified:
                return redirect('user_profile')     
        except StudentUser.DoesNotExist:
            pass
        try:
            recruiter = Recruiter.objects.get(user=request.user)
            if recruiter.type == "recruiter" and recruiter.status != "pending":
                return redirect('job_list')
        except Recruiter.DoesNotExist:
            pass


    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                refresh_token, access_token = get_tokens_for_user(user)
                request.session['access_token'] = access_token
                request.session['refresh_token'] = refresh_token
                messages.success(request, "Logged in successfully as admin.")
                return redirect('admin_profile')
            try:
                student = StudentUser.objects.get(user=user)
                if student.type == "user" and student.is_verified==True:
                    login(request, user)
                    refresh_token, access_token = get_tokens_for_user(user)
                    request.session['access_token'] = access_token
                    request.session['refresh_token'] = refresh_token
                    messages.success(request, "Logged in successfully as a student user.")
                    return redirect('user_profile')
                messages.error(request, "Your account is not verified. Please verify your email.")
                return redirect('resend_verification_email')

            except StudentUser.DoesNotExist:
                pass
            try:
                recruiter = Recruiter.objects.get(user=user)
                if recruiter.type == "recruiter" and recruiter.status == "accept":
                    login(request, user)
                    refresh_token, access_token = get_tokens_for_user(user)
                    request.session['access_token'] = access_token
                    request.session['refresh_token'] = refresh_token
                    messages.success(request, "Logged in successfully as a recruiter.")
                    return redirect('job_list')
                elif recruiter.type == "recruiter" and recruiter.status == "pending":
                    messages.info(request, "Currently your status is pending login after some time")
                    return redirect('index')
                elif recruiter.type == "recruiter" and recruiter.status == "reject":
                    messages.warning(request, "You can not login since your status is rejected")
                    return redirect('index')
            except Recruiter.DoesNotExist:
                pass
        messages.error(request, "Invalid credentials. Please try again")
    return render(request, 'login_view.html')


def resend_verification_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(username=email)
            student_user = StudentUser.objects.get(user=user)
            if not student_user.is_verified:
                otp = generate_otp()
                request.session['otp'] = otp  # Store OTP in session
                request.session['user_id'] = user.id  # Store user ID in session
                send_otp_email(email, otp)
                messages.success(request, 'A new OTP has been sent to your email. Please verify your account.')
                return redirect('verify_otp')
            else:
                messages.info(request, 'Your account is already verified. You can log in.')
                return redirect('login_view')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email. Please sign up.')
            return redirect('user_signup')
    return render(request, 'resend_verification_email.html')






import random
from django.core.mail import send_mail
from django.conf import settings
# Generate OTP
def generate_otp():
    otp=str(random.randint(100000, 999999))
    print(otp)
    return otp


def send_otp_email(email, otp):
    subject = 'Your OTP for Email Verification'
    message = f'Your OTP is {otp}. Enter this code to verify your email address.'
    from_email = settings.EMAIL_HOST_USER  # Your email address
    send_mail(subject, message, from_email, [email])


# Verify OTP
def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')  # Assuming you stored OTP in session
        if entered_otp == stored_otp:
            user_id = request.session.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                student_user = StudentUser.objects.get(user=user)
                student_user.is_verified = True
                student_user.save()
                # Clear OTP and user ID from session after verification
                del request.session['otp']
                del request.session['user_id']
                messages.success(request, 'Your account has been successfully activated. You can now log in.')
                return redirect('login_view')
            else:
                messages.error(request, 'User not found. Please sign up again.')
                return redirect('user_signup')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'verify_otp.html')

def account_activation_success(request):
    return render(request, 'account_activation_success.html')



from django.db import IntegrityError

def user_signup(request):
    if request.method == 'POST':
        f = request.POST.get('fname')
        l = request.POST.get('lname')
        image = request.FILES.get('image')
        p = request.POST.get('pwd')
        e = request.POST.get('email')
        con = request.POST.get('contact')
        gen = request.POST.get('gender')
        resume = request.FILES.get('resume') 
        try:
            
            # email = request.POST.get('email')
            otp = generate_otp()
            request.session['otp'] = otp  # Store OTP in session
            send_otp_email(e, otp)
            user = User.objects.create_user(first_name=f, last_name=l, username=e, password=p)
            StudentUser.objects.create(user=user, mobile=con, image=image, gender=gen, type="user", resume=resume)
            request.session['user_id'] = user.id  # Store user ID in session
            messages.success(request, 'You have successfully signed up. Please verify your email to activate your account.')
            return redirect('verify_otp')
        except IntegrityError:
            messages.error(request, 'A user with this email already exists.')
 
    return render(request, 'user_signup.html')

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated


def user_home(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    
    student = StudentUser.objects.get(user=request.user)
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact = request.POST.get('contact')
        gender = request.POST.get('gender')
        image = request.FILES.get('image')

        # Update recruiter's profile details
        request.user.first_name = first_name
        request.user.last_name = last_name
        student.mobile = contact
        student.gender = gender

        
        # Update image if provided
        if image:
            student.image = image
        
        # Save changes
        request.user.save()
        student.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')
    
    return render(request, 'user_home.html', {'student': student})

    

def Logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login_view')


from django.db import transaction

def recruiter_signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        image = request.FILES.get('image')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        gender = request.POST.get('gender')
        company = request.POST.get('company')
        
        # if not (first_name and last_name and password and email and contact and gender and company):
        #     messages.error(request, 'Please fill in all the required fields.')
        #     return redirect('recruiter_signup')

        try:
            with transaction.atomic():
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=email, password=password)
                Recruiter.objects.create(user=user, mobile=contact, image=image, gender=gender, type="recruiter", company=company, status="pending")
            
            messages.success(request, 'You have successfully signed up. Your login status is pending.')
            return redirect('login_view')
        except Exception as e:
            messages.error(request, 'An error occurred during signup. Please try again.')
            print(f"Error during recruiter signup: {e}")
    
    return render(request, 'recruiter_signup.html')

def recruiter_home(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    
    recruiter = Recruiter.objects.get(user=request.user)
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact = request.POST.get('contact')
        gender = request.POST.get('gender')
        image = request.FILES.get('image')
        company = request.POST.get('company')

        # Update recruiter's profile details
        request.user.first_name = first_name
        request.user.last_name = last_name
        recruiter.mobile = contact
        recruiter.gender = gender
        recruiter.company = company

        
        # Update image if provided
        if image:
            recruiter.image = image
        
        # Save changes
        request.user.save()
        recruiter.save()
        
        messages.success(request, 'Profile updated successfully!')
    
    return render(request, 'recruiter_home.html', {'recruiter': recruiter})



def view_users(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    data = StudentUser.objects.all()
    d = {'data':data}
    return render(request,'view_users.html',d)

def delete_user(request,pid):
    if not request.user.is_authenticated:
        return redirect('login_view')
    student = User.objects.get(id=pid)
    # Delete associated User then automatically StudentUser gets deleted
    student.delete()
    return redirect('view_users')

def delete_recruiter(request,pid):
    if not request.user.is_authenticated:
        return redirect('login_view')
    recruiter = User.objects.get(id=pid)
    recruiter.delete()
    return redirect('recruiter_all')

def delete_job(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_view')
    
    # Check if the job exists
    job = get_object_or_404(Job, id=pid)
    
    # Check if the logged-in user is the owner of the job
    if request.user != job.recruiter.user:
        messages.warning(request, "You are not allowed to delete this job post.")
        return redirect('job_view', pid=pid)  # Redirect if not the owner
    
    # Delete the job
    job.delete()
    
    messages.success(request, "Job deleted successfully.")
    return redirect('job_list')

def recruiter_pending(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    data = Recruiter.objects.filter(status__iexact="pending")
    if not data:
        messages.warning(request,"No pending Recruiters")
        return redirect('recruiter_all')
    d = {'data':data}
    return render(request,'recruiter_pending.html',d)

def change_status(request,pid):
    if not request.user.is_authenticated:
        return redirect('login_view')
    error=""
    recruiter = Recruiter.objects.get(id=pid)
    if request.method=="POST":
        s = request.POST['status']
        recruiter.status=s
        try:
            recruiter.save()
            error="no"
        except:
            error="yes"
    d = {'recruiter':recruiter,'error':error}
    return render(request,'change_status.html',d)

def recruiter_accepted(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    data = Recruiter.objects.filter(status__iexact="accept")
    if not data:
        messages.info(request,"No Accepted Recruiters")
        return redirect('recruiter_all')
    d = {'data':data}
    return render(request,'recruiter_accepted.html',d)

def recruiter_rejected(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    data = Recruiter.objects.filter(status__iexact="reject")
    if not data:
        messages.warning(request,"Currently there are no Rejected Recruiters")
        return redirect('recruiter_all')
    d = {'data':data}
    return render(request,'recruiter_rejected.html',d)

def recruiter_all(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    data = Recruiter.objects.all()
    d = {'data':data}
    return render(request,'recruiter_all.html',d)

@login_required
def change_password(request):
    if not request.user.is_authenticated:
        return redirect('login_view')  # Redirect to login page if user is not authenticated
    user_type=None
    try:
        student_user = StudentUser.objects.get(user=request.user)
        user_type = student_user.type
    except StudentUser.DoesNotExist:
        try:
            recruiter = Recruiter.objects.get(user=request.user)
            user_type = recruiter.type
        except Recruiter.DoesNotExist:
            user_type='admin'

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        # Verify current password
        if request.user.check_password(current_password):
            # Check if new password and confirm new password match
            if new_password == confirm_new_password:
                # Set new password for the user
                request.user.set_password(new_password)
                request.user.save()

                # Update the user's session to prevent logout
                update_session_auth_hash(request, request.user)

                # Redirect to a success page or return a success message
                messages.success(request, f"Password updated successfully for {user_type.capitalize()}!")

                if user_type == 'user':
                    return redirect('user_profile')
                elif user_type == 'recruiter':
                    return redirect('recruiter_profile')
                else:
                    return redirect('admin_profile')
            else:
                # Return an error message indicating password mismatch
                return render(request, 'change_password.html', {'error': 'New password and confirm new password do not match.'})
        else:
            # Return an error message indicating incorrect current password
            return render(request, 'change_password.html', {'error': 'Incorrect current password.'})

    return render(request, 'change_password.html', {'user_type': user_type})


def job_add(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    error = ""
    if request.method == 'POST':
        # Retrieve form data
        title = request.POST.get('job_title')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        salary = request.POST.get('salary')
        image = request.FILES.get('logo')
        experience = request.POST.get('experience')
        location = request.POST.get('location')
        skills = request.POST.get('skills')
        description = request.POST.get('description')
        eligibility_criteria = request.POST.get('eligibility_criteria')
        job_type = request.POST.get('job_type')
        process = request.POST.get('process')
        role_responsibilities = request.POST.get('role_responsibilities')
        mode_of_work = request.POST.get('mode_of_work')
        # Create a new job entry in the database
        try:
            job = Job.objects.create(
                recruiter=Recruiter.objects.get(user=request.user),
                title=title,
                start_date=start_date,
                end_date=end_date,
                salary=salary,
                image=image,
                description=description,
                experience=experience,
                location=location,
                skills=skills,
                eligibility_criteria=eligibility_criteria,
                job_type=job_type,
                process=process,
                role_responsibilities=role_responsibilities,
                mode_of_work=mode_of_work,
                creation_date= date.today(),
            )
            messages.success(request,"Added your job!!")
            error = "no"
        except Exception as e:
            print(e)
            error = "yes"

    d = {'error': error}
    return render(request, 'job_add.html')



def job_list(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    user= request.user # to get the current user
    recruiter=Recruiter.objects.get(user=user)
    job=Job.objects.filter(recruiter=recruiter)
    d={'job':job}
    return render(request,'job_list.html',d)


def job_edit(request,pid):
    if not request.user.is_authenticated:
        return redirect('login_view')
    
    error=""
    job = get_object_or_404(Job, id=pid)

     # Check if the logged-in user is the owner of the job
    if request.user != job.recruiter.user:
        messages.warning(request,"you are not allowed here !! since you have't posted this")
        return redirect('job_view', pid=pid)  # Redirect if not the owner
    
    if request.method == 'POST':
        # Retrieve form data
        title = request.POST.get('job_title')
        salary = request.POST.get('salary')
        image = request.FILES.get('logo')
        experience = request.POST.get('experience')
        location = request.POST.get('location')
        skills = request.POST.get('skills')
        description = request.POST.get('description')
        eligibility_criteria = request.POST.get('eligibility_criteria')
        job_type = request.POST.get('job_type')
        process = request.POST.get('process')
        role_responsibilities = request.POST.get('role_responsibilities')
        mode_of_work = request.POST.get('mode_of_work')

        # Update the job entry in the database
        try:
            job.title = title
            job.salary = salary
            if image:
                job.image = image
            job.experience = experience
            job.location = location
            job.skills = skills
            job.description = description
            if request.POST.get('start_date'):
                job.start_date = request.POST.get('start_date')
            if request.POST.get('end_date'):
                job.end_date = request.POST.get('end_date')
            job.eligibility_criteria = eligibility_criteria
            job.job_type = job_type
            job.process = process
            job.role_responsibilities = role_responsibilities
            job.mode_of_work = mode_of_work
            job.save()

            messages.success(request, "Job details updated successfully")
            return redirect('job_view', pid=job.id)
        except Exception as e:
            print(e)
            error = "yes"

    d = {'error': error, 'job': job}
    return render(request, 'job_edit.html',d)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def job_view(request, pid):
    user_type = None
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
    try:
        job = Job.objects.get(id=pid)
    except Job.DoesNotExist:
        return render(request, 'latest_jobs.html', {'error_message': 'Job does not exist'})
    li=[]
    if user_type == 'user':
        student = StudentUser.objects.get(user=request.user)
        data = Apply.objects.filter(student=student)   
        for i in data:
            li.append(i.job.id) # here job is variable fro Apply model
    
    return render(request, 'job_view.html', {'job': job, 'user_type': user_type,'li':li})


def latest_jobs(request):
    jobs=Job.objects.all().order_by('-start_date')
    d={'jobs':jobs,'today_date':date.today()}
    return render(request,'latest_jobs.html',d)


from django.db.models import Case, When, Value, IntegerField

def user_latest_jobs(request):
    # jobs=Job.objects.all().order_by('-start_date')
    # Order jobs by start date and handle end date dynamically
    jobs = Job.objects.annotate(
        sort_order=Case(
            # If end date is in the future, sort by start date
            When(end_date__gte=timezone.now(), then=Value(1)),
            # If end date is in the past, sort by end date
            default=Value(2),
            output_field=IntegerField(),
        )
    ).order_by('sort_order', 'start_date', 'end_date')
    user = request.user
    student = StudentUser.objects.get(user=user)
    data = Apply.objects.filter(student=student)
    li=[]
    for i in data:
        li.append(i.job.id) # here job is variable fro Apply model
    page="home"
    
    d={'jobs':jobs,'li':li,'page':page,'Todate':date.today()}
    return render(request,'user_latest_jobs.html',d)

def job_detail(request,pid):
    job=Job.objects.get(id=pid)
    d={'job':job}
    return render(request,'job_detail.html',d)

from django.utils import timezone

def apply_for_job(request,pid):
    if not request.user.is_authenticated:
        return redirect('login_view')
    
    user = request.user
    student = StudentUser.objects.get(user=user)
    job = Job.objects.get(id=pid)
    date_today = date.today()
    if job.end_date < date_today:
        messages.error(request,"Application closed")
        return redirect('user_latest_jobs')
    elif job.start_date > date_today:
        messages.warning(request,"Not opened")
        return redirect('user_latest_jobs')
    else:
        if request.method == 'POST':
            new_resume = request.FILES.get('new_resume')  # Get the uploaded resume
            if new_resume:
                # If a new resume is uploaded, use it
                apply_instance = Apply.objects.create(job=job, student=student, resume=new_resume, apply_date=date_today)
                student.resume = new_resume
                student.save()
                messages.success(request, "Applied successfully with the new resume")
            else:
                # If no new resume is uploaded, use the old one
                apply_instance = Apply.objects.create(job=job, student=student, resume=student.resume, apply_date=date_today)
                messages.success(request, "Applied successfully with the old resume")
            
            return redirect('user_latest_jobs')
    d={'student':student,'job':job}
    return render(request,'apply_for_job.html',d) 

def applied_candidates_list(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    
    data = Apply.objects.all().order_by('job__title', '-apply_date')
    d ={'data':data}
    return render(request,'applied_candidates_list.html',d)
 
# code to get the candidates applied for a specific job  
def applied_candidates_job(request, job_id):
    # Retrieve the job object
    job = get_object_or_404(Job, id=job_id)
    # Retrieve all job applications related to the job
    job_applications = Apply.objects.filter(job=job)
    return render(request, 'applied_candidates_job.html', {'job': job, 'job_applications': job_applications})


from .forms import JobSearchForm

def job_search(request):
    user_type = None
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
    if request.method == 'POST':
        form = JobSearchForm(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data.get('keyword')
            location = form.cleaned_data.get('location')
            experience = form.cleaned_data.get('experience')

            # Construct query based on search criteria
            jobs = Job.objects.all()
            if keyword:
                jobs = jobs.filter(title__icontains=keyword)
            if location:
                jobs = jobs.filter(location__icontains=location)
            if experience:
                min_exp, max_exp = [int(exp.strip()) for exp in experience.split('-')]
                jobs = jobs.filter(experience__gte=min_exp, experience__lte=max_exp)

            return render(request, 'index.html', {'jobs': jobs,'user_type': user_type})
    else:
        form = JobSearchForm()

    return render(request, 'job_search.html', {'form': form})


#profiles


# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
def user_profile(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    student = StudentUser.objects.get(user=request.user)
    return render(request,'user_profile.html',{'student':student})


def recruiter_profile(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    
    recruiter = Recruiter.objects.get(user=request.user)
    return render(request,'recruiter_profile.html',{'recruiter':recruiter})


def admin_profile(request):
    user = request.user
    return render(request, 'admin_profile.html', {'user': user})




def accept_or_reject_application(request, application_id, action):
    application = get_object_or_404(Apply, id=application_id)
    if action == 'accept':
        application.status = 'accepted'
        messages.success(request, 'Application accepted successfully.')
    elif action == 'reject':
        application.status = 'rejected'
        messages.warning(request, 'Application rejected successfully.')
    application.save()
    return redirect('applied_candidates_list')  # Redirect to the applied candidates page


from rest_framework.views import APIView
from .serializer import *
from rest_framework.response import Response
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken
class LoginAPI(APIView):
    
    def post(self, request):
        try:
            data = request.data
            serializer = LoginSerializer(data = data)
            if  serializer.is_valid():
                username = serializer.data['username']
                password = serializer.data['password']

                user = authenticate(username = username,password = password)

                if user is None:

                    return Response ({
                    'status':400,
                    'message' : 'Invalid  password !!',
                    'data' :serializer.errors
                     })

                # if login credentials are correct it create a token
                refresh = RefreshToken.for_user(user)

                return {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }


            return Response ({
                'status':400,
                'message' : 'something went wrong',
                'data' :serializer.errors
            })
        except Exception as e:
            print(e)

# from rest_framework_simplejwt.views import TokenObtainPairView

# class ObtainTokenPairWithUsernameView(TokenObtainPairView):
#     serializer_class = ObtainTokenPairSerializer



from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        return Response(data, status=status.HTTP_200_OK)
    


    