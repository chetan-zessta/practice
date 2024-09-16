from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import StudentUser, Recruiter

class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', password='123', is_staff=True)
        self.student_user = User.objects.create_user(username='student', password='123')
        self.recruiter_user = User.objects.create_user(username='recruiter', password='123')
        
        StudentUser.objects.create(user=self.student_user, type="user", is_verified=True)
        Recruiter.objects.create(user=self.recruiter_user, type="recruiter", status="accept")

    def test_admin_login(self):
        response = self.client.post(reverse('login_view'), {'username': 'admin', 'password': '123'})
        self.assertRedirects(response, reverse('admin_profile'))

    def test_verified_student_login(self):
        response = self.client.post(reverse('login_view'), {'username': 'student', 'password': '123'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user_profile'))

    def test_accepted_recruiter_login(self):
        response = self.client.post(reverse('login_view'), {'username': 'recruiter', 'password': '123'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('job_list'))

    def test_invalid_login(self):
        response = self.client.post(reverse('login_view'), {'username': 'invalid', 'password': 'invalidpass'})
        self.assertContains(response, "Invalid credentials. Please try again")

    def test_unverified_student_login(self):
        unverified_student = User.objects.create_user(username='unverified_student', password='123')
        StudentUser.objects.create(user=unverified_student, type="user", is_verified=False)
        response = self.client.post(reverse('login_view'), {'username': 'unverified_student', 'password': '123'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('resend_verification_email'))
    def test_pending_recruiter_login(self):
        pending_recruiter = User.objects.create_user(username='pending_recruiter', password='123')
        Recruiter.objects.create(user=pending_recruiter, type="recruiter", status="pending")
        response = self.client.post(reverse('login_view'), {'username': 'pending_recruiter', 'password': '123'})
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertRedirects(response, '/')  # Redirecting back to the home page

    def test_rejected_recruiter_login(self):
        rejected_recruiter = User.objects.create_user(username='rejected_recruiter', password='123')
        Recruiter.objects.create(user=rejected_recruiter, type="recruiter", status="reject")
        response = self.client.post(reverse('login_view'), {'username': 'rejected_recruiter', 'password': '123'})
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertRedirects(response, '/')  # Redirecting back to the home page




class UserIntegrationTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', password='123', is_staff=True)
        self.student_user = User.objects.create_user(username='student', password='123')
        self.recruiter_user = User.objects.create_user(username='recruiter', password='123')
        
        StudentUser.objects.create(user=self.student_user, type="user", is_verified=True)
        Recruiter.objects.create(user=self.recruiter_user, type="recruiter", status="accept")

    def test_admin_login_and_access(self):
        response = self.client.post(reverse('login_view'), {'username': 'admin', 'password': '123'})
        self.assertRedirects(response, reverse('admin_profile'))

    def test_student_login_and_access(self):
        response = self.client.post(reverse('login_view'), {'username': 'student', 'password': '123'})
        self.assertRedirects(response, reverse('user_profile'))

    def test_recruiter_login_and_access(self):
        response = self.client.post(reverse('login_view'), {'username': 'recruiter', 'password': '123'})
        self.assertRedirects(response, reverse('job_list'))

    def test_create_student_user_via_signup(self):
        response = self.client.post(reverse('user_signup'), {
            'fname': 'Jane',
            'lname': 'Doe',
            'pwd': 'password123',
            'email': 'jane.doe@example.com',
            'contact': '0987654321',
            'gender': 'F'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to OTP verification view
        self.assertTrue(User.objects.filter(username='jane.doe@example.com').exists())
        self.assertTrue(StudentUser.objects.filter(user__username='jane.doe@example.com').exists())

    def test_create_recruiter_via_signup(self):
        response = self.client.post(reverse('recruiter_signup'), {
            'fname': 'John',
            'lname': 'Doe',
            'pwd': 'password123',
            'email': 'john.doe@example.com',
            'contact': '1234567890',
            'gender': 'M',
            'company': 'TechCorp'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login view
        self.assertTrue(User.objects.filter(username='john.doe@example.com').exists())
        self.assertTrue(Recruiter.objects.filter(user__username='john.doe@example.com').exists())
