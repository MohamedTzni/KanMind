from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import RegistrationSerializer, LoginSerializer


def get_user_response(token, user):
    """Return user data dict for auth responses."""
    full_name = f"{user.first_name} {user.last_name}".strip()
    display_name = full_name or user.username

    return {
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
        'fullname': full_name,
        'name': display_name,   # <-- DAS fehlt deinem Frontend!
        'email': user.email,
    }




class RegistrationView(APIView):
    """User Registration View"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get(user=user)
            return Response(get_user_response(token, user), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User Login View"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response(get_user_response(token, user), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """User Logout View"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Delete user token to logout"""
        try:
            request.user.auth_token.delete()
            return Response(
                {'message': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {'error': 'Something went wrong.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileView(APIView):
    """Get current user profile"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return current user data"""
        user = request.user
        return Response({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'fullname': f"{user.first_name} {user.last_name}".strip(),
            'date_joined': user.date_joined,
        }, status=status.HTTP_200_OK)


class EmailCheckView(APIView):
    """Check if an email address is already registered."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return user data if email exists, 404 otherwise."""
        email = request.query_params.get('email', '')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        fullname = f"{user.first_name} {user.last_name}"
        return Response({
            'id': user.id,
            'email': user.email,
            'fullname': fullname.strip(),
        }, status=status.HTTP_200_OK)
    

class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "name": f"{user.first_name} {user.last_name}".strip() or user.username,
            "email": user.email,
        })
