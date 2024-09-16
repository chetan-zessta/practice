from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
# TYPE_CHOICES = (
#         ('cust_user', 'User'),
#         ('recruiter', 'Recruiter'),
#     )
class StudentUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    image = models.ImageField( blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    type = models.CharField(max_length=10, blank=True, null=True)
    resume= models.FileField(upload_to='resumes/',blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.username} - {self.type}'
    

about_company_default = "Welcome to our company! We are dedicated to providing innovative solutions and excellent services to our clients. Our team consists of talented professionals who are passionate about their work and committed to achieving our company's goals. With a focus on quality and customer satisfaction, we strive to exceed expectations in everything we do. Explore our website to learn more about our company and the exciting opportunities we offer."

class Recruiter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    image = models.ImageField(blank=True,null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    type = models.CharField(max_length=10, blank=True, null=True)
    company=models.CharField(max_length=50,null=True)
    about_company=models.CharField(max_length=100,default=about_company_default)
    status = models.CharField(max_length=20,null=True)
    def __str__(self):
        return f'{self.user.username} - {self.company}'
    

class Job(models.Model):
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    title = models.CharField(max_length=100)
    salary = models.CharField(max_length=20)
    image=models.ImageField(blank=True, null=True)
    description = models.TextField()
    experience = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    skills = models.CharField(max_length=100)
    eligibility_criteria = models.CharField(max_length=300, default="No specific eligibility criteria provided")
    job_type = models.CharField(max_length=100, default="Full-time")
    process = models.CharField(max_length=300, default="Standard application process")
    role_responsibilities = models.CharField(max_length=500, default="Software developer, Designing, coding, testing, and debugging software applications")
    mode_of_work = models.CharField(max_length=10,default="on-site")
    creation_date = models.DateField()

    def __str__(self):
        return self.title    
    

class Apply(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentUser, on_delete=models.CASCADE)
    resume=models.FileField(null=True)
    apply_date = models.DateField()
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')

    def __str__(self):
        return str(self.job.title +" by "+ self.student.user.first_name)   