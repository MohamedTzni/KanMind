from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from auth_app.api.serializers import RegistrationSerializer, LoginSerializer


class RegistrationView(APIView):
    """User Registration View"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Register new user and return token"""
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get(user=user)
            
            return Response({
                'token': token.key,
                'user_id': user.id,
                'fullname': f"{user.first_name} {user.last_name}".strip(),
                'email': user.email,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User Login View"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate user and return token"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user_id': user.id,
                'fullname': f"{user.first_name} {user.last_name}".strip(),
                'email': user.email,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)