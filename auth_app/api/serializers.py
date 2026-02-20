from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.authtoken.models import Token


class RegistrationSerializer(serializers.Serializer):
    """Serializer for user registration."""
    fullname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """Check that the email is not already in use."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )
        return value

    def validate(self, data):
        """Check that both passwords match."""
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                "Passwords do not match."
            )
        return data

    def parse_name(self, fullname):
        """Split a full name into first and last name."""
        name_parts = fullname.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        return first_name, last_name

    def create(self, validated_data):
        """Create a new user and generate an auth token."""
        first_name, last_name = self.parse_name(
            validated_data['fullname']
        )
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
        )
        Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Check email and password and attach user to data."""
        email = data['email']
        password = data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid credentials."
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                "Invalid credentials."
            )

        data['user'] = user
        return data
