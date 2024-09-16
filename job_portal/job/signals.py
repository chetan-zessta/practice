# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import *


@receiver(post_save, sender=StudentUser)
def send_welcome_email_to_student(sender, instance, created, **kwargs):
    if created:
        student_email = instance.user.username
        student_name = instance.user.first_name
        send_mail(
            subject='Welcome to Our Job Portal',
            message=f'Dear {student_name},\n\nThank you for signing up.\nYou can now apply for jobs on our platform.\n\nBest regards,\nchetan pediredla',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[student_email],
            fail_silently=False,
        )

@receiver(post_save, sender=Recruiter)
def send_welcome_email_to_recruiter(sender, instance, created, **kwargs):
    if created:
        recruiter_email = instance.user.username
        recruiter_name = instance.user.first_name
        company_name = instance.company
        send_mail(
            subject='Welcome to Our Job Portal',
            message=f'Dear {recruiter_name},\n\nThank you for signing up. You can now post jobs form your company, {company_name}, on our platform.\n\nBest regards,\nChetan Pediredla',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recruiter_email],
            fail_silently=False,
        )

@receiver(post_save, sender=Apply)
def send_application_email(sender, instance, created, **kwargs):
    if created:
        # Sending mail to the student user
        student_email = instance.student.user.username if instance.student.user.username else ''  # Ensure email attribute exists
        if student_email:
            job_title = instance.job.title
            send_mail(
                subject=f'Application Submitted for {job_title}',
                message=f'Dear {instance.student.user.first_name},\n\n Your application for the job "{job_title}" has been submitted on {instance.apply_date} successfully and is under review.visit our website for further updates.\n\nBest regards,\nChetan Pediredla',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[student_email],
                fail_silently=False,
            )

        # Sending mail to the recruiter
        recruiter_email = instance.job.recruiter.user.username if instance.job.recruiter.user.username else ''  # Ensure email attribute exists
        if recruiter_email:
            job_title = instance.job.title
            send_mail(
                subject=f'New Job Application for {job_title}',
                message=f'Hello Recruiter,\n\nYou have a new job application from {instance.student.user.first_name} for the position of {job_title}.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recruiter_email],
                fail_silently=False,
            )
        
