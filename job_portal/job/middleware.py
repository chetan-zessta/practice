# middleware.py
import logging
from django.shortcuts import redirect
from django.urls import reverse,resolve

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('django.request')

    def __call__(self, request):
        # Log the request details
        self.logger.info(f'Testing middleware \nRequest Method: {request.method}, URL: {request.get_full_path()}')
        response = self.get_response(request)
        return response

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_paths = [
            '/login_view/', 
            '/user_signup/', 
            '/recruiter_signup/', 
            '/latest_jobs/', 
            reverse('index')
        ]
        
        # Check if the user is authenticated or if the path is in the allowed paths
        if not request.user.is_authenticated:
            resolved_url = resolve(request.path_info)
            # Check if the resolved URL name is 'job_view'
            if resolved_url.url_name == 'job_view':
                # Allow access to job_view regardless of authentication
                response = self.get_response(request)
                return response
            
            if request.path not in allowed_paths:
                return redirect('/login_view/')
        
        response = self.get_response(request)
        return response