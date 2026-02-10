from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class RegistrationAPITest(TestCase):
    """Test user registration"""
    
    def setUp(self):
        """Setup test client"""
        self.client = APIClient()
    
    def test_registration_success(self):
        """Test successful user registration"""
        data = {
            'fullname': 'John Doe',
            'email': 'john@example.com',
            'password': 'secure123',
            'repeated_password': 'secure123'
        }
        response = self.client.post('/api/registration/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['email'], 'john@example.com')
        
        # Check user was created
        self.assertTrue(User.objects.filter(email='john@example.com').exists())
    
    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            'fullname': 'John Doe',
            'email': 'john@example.com',
            'password': 'secure123',
            'repeated_password': 'different123'
        }
        response = self.client.post('/api/registration/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_registration_duplicate_email(self):
        """Test registration with existing email"""
        User.objects.create_user(
            username='existing',
            email='john@example.com',
            password='pass'
        )
        data = {
            'fullname': 'John Doe',
            'email': 'john@example.com',
            'password': 'secure123',
            'repeated_password': 'secure123'
        }
        response = self.client.post('/api/registration/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_registration_missing_fields(self):
        """Test registration with missing fields"""
        data = {
            'email': 'john@example.com',
            'password': 'secure123'
        }
        response = self.client.post('/api/registration/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITest(TestCase):
    """Test user login"""
    
    def setUp(self):
        """Create test user and client"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_login_success(self):
        """Test successful login"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post('/api/login/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent email"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/login/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        data = {'email': 'test@example.com'}
        response = self.client.post('/api/login/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutAPITest(TestCase):
    """Test user logout"""
    
    def setUp(self):
        """Create authenticated user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_logout_success(self):
        """Test successful logout"""
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check token was deleted
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())
    
    def test_logout_unauthorized(self):
        """Test logout without authentication"""
        self.client.credentials()  # Remove credentials
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileAPITest(TestCase):
    """Test user profile endpoint"""
    
    def setUp(self):
        """Create authenticated user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_get_profile_success(self):
        """Test getting user profile"""
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['username'], 'testuser')
        self.assertIn('fullname', response.data)
    
    def test_get_profile_unauthorized(self):
        """Test getting profile without authentication"""
        self.client.credentials()  # Remove credentials
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EmailCheckAPITest(TestCase):
    """Test email check endpoint."""

    def setUp(self):
        """Create test user and authenticated client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )

    def test_email_exists(self):
        """Test checking an email that exists."""
        url = '/api/email-check/?email=test@example.com'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['fullname'], 'Test User')

    def test_email_does_not_exist(self):
        """Test checking an email that does not exist."""
        url = '/api/email-check/?email=unknown@example.com'
        response = self.client.get(url)
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_email_check_no_param(self):
        """Test checking without email parameter."""
        response = self.client.get('/api/email-check/')
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_email_check_unauthorized(self):
        """Test email check without authentication."""
        self.client.credentials()
        response = self.client.get('/api/email-check/')
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )


class UserMeAPITest(TestCase):
    """Test user-me endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='meuser', password='password', email='me@example.com')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_user_me_success(self):
        """Test GET /api/users/me/"""
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'me@example.com')


class FormattedFullNameTest(TestCase):
    """Test get_formatted_fullname edge cases"""

    def test_fullname_only_username(self):
        user = User(username='onlyuser')
        from auth_app.api.views import get_formatted_fullname
        fullname = get_formatted_fullname(user)
        self.assertEqual(fullname, 'onlyuser onlyuser')

    def test_fullname_only_first(self):
        user = User(username='firstuser', first_name='John')
        from auth_app.api.views import get_formatted_fullname
        fullname = get_formatted_fullname(user)
        self.assertEqual(fullname, 'John John')

    def test_fullname_only_last(self):
        user = User(username='lastuser', last_name='Doe')
        from auth_app.api.views import get_formatted_fullname
        fullname = get_formatted_fullname(user)
        self.assertEqual(fullname, 'Doe Doe')