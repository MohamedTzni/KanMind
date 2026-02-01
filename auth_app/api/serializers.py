from rest_framework import serializers
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles password validation and user creation.
    """
    fullname = serializers.CharField(write_only=True, max_length=150)
    repeated_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        """Check if email already exists."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, attrs):
        """Check if passwords match."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        """Create new user with hashed password."""
        fullname = validated_data.pop('fullname')
        validated_data.pop('repeated_password')
        
        # Use fullname as username
        username = fullname.replace(' ', '_').lower()
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Split fullname into first_name and last_name
        name_parts = fullname.split(' ', 1)
        user.first_name = name_parts[0]
        if len(name_parts) > 1:
            user.last_name = name_parts[1]
        user.save()
        
        return user