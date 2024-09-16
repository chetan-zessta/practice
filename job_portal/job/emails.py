# import random
# from django.core.mail import send_mail
# from django.conf import settings



# def send_otp_email(email):
#     subject = 'Your OTP for Email Verification'
#     otp=str(random.randint(1000, 9999))
#     message = f'Your OTP is {otp}. Enter this code to verify your email address.'
#     # from_email = 'naniemma123@gmail.com'  # Your email address
#     email_from = settings.EMAIL_HOST
#     send_mail(subject, message, email_from, [email])