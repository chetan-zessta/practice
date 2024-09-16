from rest_framework import serializers
from django.contrib.auth.models import User
from .models import StudentUser, Recruiter

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Add other fields as needed

class StudentUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = StudentUser
        fields = ['id', 'user', 'mobile', 'image', 'gender', 'type', 'resume']  # Add other fields as needed

class RecruiterSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Recruiter
        fields = ['id', 'user', 'mobile', 'image', 'gender', 'type', 'company', 'about_company', 'status']  # Add other fields as needed



class LoginSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField()
