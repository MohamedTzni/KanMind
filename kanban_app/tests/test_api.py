from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from kanban_app.models import Board, Ticket, Comment


class BoardAPITest(TestCase):
    """Test Board API endpoints"""

    def setUp(self):
        """Create test data and authenticate"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.board = Board.objects.create(
            title='Test Board',
            description='Test Description',
            owner=self.user
        )

    def test_list_boards(self):
        """Test listing boards"""
        response = self.client.get('/api/boards/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['description'], 'Test Description')

    def test_create_board(self):
        """Test creating a board"""
        data = {'title': 'New Board', 'description': 'New Board Description'}
        response = self.client.post('/api/boards/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Board')
        self.assertEqual(response.data['description'], 'New Board Description')
        self.assertEqual(response.data['owner_id'], self.user.id)

    def test_retrieve_board(self):
        """Test retrieving a single board"""
        response = self.client.get(f'/api/boards/{self.board.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Board')
        self.assertEqual(response.data['description'], 'Test Description')

    def test_update_board(self):
        """Test updating a board"""
        data = {'title': 'Updated Board', 'description': 'Updated Description'}
        response = self.client.patch(f'/api/boards/{self.board.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Board')
        self.assertEqual(response.data['description'], 'Updated Description')

    def test_delete_board(self):
        """Test deleting a board"""
        response = self.client.delete(f'/api/boards/{self.board.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Board.objects.count(), 0)

    def test_board_access_denied_other_user(self):
        """Test that other users cannot access board"""
        other_user = User.objects.create_user(username='other', password='pass')
        other_token = Token.objects.create(user=other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {other_token.key}')

        response = self.client.get(f'/api/boards/{self.board.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TicketAPITest(TestCase):
    """Test Ticket API endpoints"""

    def setUp(self):
        """Create test data and authenticate"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.board = Board.objects.create(title='Test Board', owner=self.user)
        self.ticket = Ticket.objects.create(
            board=self.board,
            title='Test Ticket',
            description='Test Description',
            status='to-do',
            priority='medium',
            created_by=self.user
        )

    def test_list_tickets(self):
        """Test listing tickets"""
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_ticket(self):
        """Test creating a ticket"""
        data = {
            'board': self.board.id,
            'title': 'New Ticket',
            'description': 'New Description',
            'status': 'to-do',
            'priority': 'high',
        }
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Ticket')

    def test_retrieve_ticket(self):
        """Test retrieving a single ticket"""
        response = self.client.get(f'/api/tasks/{self.ticket.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Ticket')

    def test_update_ticket(self):
        """Test updating a ticket"""
        data = {'status': 'in-progress', 'priority': 'high'}
        response = self.client.patch(f'/api/tasks/{self.ticket.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Ticket')

    def test_delete_ticket(self):
        """Test deleting a ticket"""
        response = self.client.delete(f'/api/tasks/{self.ticket.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ticket.objects.count(), 0)


class CommentAPITest(TestCase):
    """Test Comment API endpoints"""

    def setUp(self):
        """Create test data and authenticate"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.board = Board.objects.create(title='Test Board', owner=self.user)
        self.ticket = Ticket.objects.create(
            board=self.board,
            title='Test Ticket',
            created_by=self.user
        )
        self.comment = Comment.objects.create(
            ticket=self.ticket,
            author=self.user,
            text='Test Comment'
        )

    def test_list_comments(self):
        """Test listing comments"""
        response = self.client.get('/api/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_comment(self):
        """Test creating a comment"""
        data = {'ticket': self.ticket.id, 'content': 'New Comment'}
        response = self.client.post('/api/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'New Comment')

    def test_retrieve_comment(self):
        """Test retrieving a single comment"""
        response = self.client.get(f'/api/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Test Comment')

    def test_delete_comment(self):
        """Test deleting a comment"""
        response = self.client.delete(f'/api/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)


class AssignedToMeAPITest(TestCase):
    """Test assigned-to-me endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.board = Board.objects.create(title='Test Board', owner=self.user)
        self.ticket = Ticket.objects.create(
            board=self.board,
            title='Assigned Ticket',
            status='to-do',
            created_by=self.user,
            assignee=self.user,
        )
        self.other_ticket = Ticket.objects.create(
            board=self.board,
            title='Other Ticket',
            status='to-do',
            created_by=self.user
        )

    def test_assigned_to_me(self):
        """Test getting tickets assigned to current user"""
        response = self.client.get('/api/tasks/assigned-to-me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Assigned Ticket')

    def test_assigned_to_me_unauthorized(self):
        """Test that unauthenticated users cannot access"""
        self.client.credentials()
        response = self.client.get('/api/tasks/assigned-to-me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewingTasksAPITest(TestCase):
    """Test reviewing tickets endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.board = Board.objects.create(title='Test Board', owner=self.user)
        self.reviewing_ticket = Ticket.objects.create(
            board=self.board,
            title='Reviewing Ticket',
            status='review',
            created_by=self.user
        )
        self.todo_ticket = Ticket.objects.create(
            board=self.board,
            title='Todo Ticket',
            status='to-do',
            created_by=self.user
        )

    def test_reviewing_tickets(self):
        """Test getting tickets with review status"""
        response = self.client.get('/api/tasks/reviewing/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Reviewing Ticket')

    def test_reviewing_tickets_unauthorized(self):
        """Test that unauthenticated users cannot access"""
        self.client.credentials()
        response = self.client.get('/api/tasks/reviewing/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticationTest(TestCase):
    """Test authentication without token"""

    def setUp(self):
        """Create unauthenticated client"""
        self.client = APIClient()

    def test_list_boards_unauthorized(self):
        """Test that unauthenticated users cannot list boards"""
        response = self.client.get('/api/boards/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_board_unauthorized(self):
        """Test that unauthenticated users cannot create boards"""
        data = {'title': 'New Board'}
        response = self.client.post('/api/boards/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class NestedCommentAPITest(TestCase):
    """Test nested comment actions within TicketViewSet"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.board = Board.objects.create(title='Test Board', owner=self.user)
        self.ticket = Ticket.objects.create(
            board=self.board, title='Test Ticket', created_by=self.user
        )
        self.comment = Comment.objects.create(
            ticket=self.ticket, author=self.user, text='Old Comment'
        )

    def test_nested_list_comments(self):
        """Test GET /api/tasks/<id>/comments/"""
        url = f'/api/tasks/{self.ticket.id}/comments/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_nested_create_comment(self):
        """Test POST /api/tasks/<id>/comments/"""
        url = f'/api/tasks/{self.ticket.id}/comments/'
        data = {'content': 'New Nested Comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'New Nested Comment')

    def test_nested_delete_comment(self):
        """Test DELETE /api/tasks/<id>/comments/<id>/"""
        url = f'/api/tasks/{self.ticket.id}/comments/{self.comment.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_nested_delete_comment_not_found(self):
        """Test DELETE nested comment with non-existent id"""
        url = f'/api/tasks/{self.ticket.id}/comments/999/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nested_delete_comment_unauthorized(self):
        """Test that other users cannot delete someone else's comment"""
        other_user = User.objects.create_user(username='other', password='password')
        other_token = Token.objects.create(user=other_user)
        self.board.members.add(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {other_token.key}')

        url = f'/api/tasks/{self.ticket.id}/comments/{self.comment.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SerializerEdgeCaseTest(TestCase):
    """Test UserSerializer edge cases for coverage"""

    def setUp(self):
        self.client = APIClient()

    def test_user_serializer_fullname_no_names(self):
        """Test get_fullname with only username set"""
        user = User.objects.create_user(username='onlyuser', password='password')
        from kanban_app.api.serializers import UserSerializer
        fullname = UserSerializer().get_fullname(user)
        self.assertEqual(fullname, 'onlyuser onlyuser')

    def test_user_serializer_fullname_only_first(self):
        """Test get_fullname with only first_name set"""
        user = User.objects.create_user(
            username='firstuser', password='password', first_name='John'
        )
        from kanban_app.api.serializers import UserSerializer
        fullname = UserSerializer().get_fullname(user)
        self.assertEqual(fullname, 'John John')

    def test_user_serializer_fullname_only_last(self):
        """Test get_fullname with only last_name set"""
        user = User.objects.create_user(
            username='lastuser', password='password', last_name='Doe'
        )
        from kanban_app.api.serializers import UserSerializer
        fullname = UserSerializer().get_fullname(user)
        self.assertEqual(fullname, 'Doe Doe')
