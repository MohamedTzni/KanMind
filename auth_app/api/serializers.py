from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class RegistrationSerializer(serializers.ModelSerializer):
    """User Registration Serializer"""
    fullname = serializers.CharField(write_only=True, max_length=150)
    repeated_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    
    def validate(self, attrs):
        """Check if passwords match"""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    
    def create(self, validated_data):
        """Create new user with token"""
        fullname = validated_data.pop('fullname')
        validated_data.pop('repeated_password')
        
        username = fullname.replace(' ', '_').lower()
        
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        name_parts = fullname.split(' ', 1)
        user.first_name = name_parts[0]
        if len(name_parts) > 1:
            user.last_name = name_parts[1]
        user.save()
        
        Token.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    """User Login Serializer"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate email and password"""
        from django.contrib.auth import authenticate
        
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        user = authenticate(username=user.username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid credentials.")
        
        attrs['user'] = user
        return attrs