from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from kanban_app.models import Board, Task, Comment


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
            owner=self.user
        )
    
    def test_list_boards(self):
        """Test listing boards"""
        response = self.client.get('/api/boards/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_board(self):
        """Test creating a board"""
        data = {'title': 'New Board'}
        response = self.client.post('/api/boards/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Board')
        self.assertEqual(response.data['owner'], self.user.id)
    
    def test_retrieve_board(self):
        """Test retrieving a single board"""
        response = self.client.get(f'/api/boards/{self.board.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Board')
    
    def test_update_board(self):
        """Test updating a board"""
        data = {'title': 'Updated Board'}
        response = self.client.put(f'/api/boards/{self.board.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Board')
    
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


class TaskAPITest(TestCase):
    """Test Task API endpoints"""
    
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
            owner=self.user
        )
        self.task = Task.objects.create(
            board=self.board,
            title='Test Task',
            description='Test Description',
            status='to-do',
            priority='medium',
            created_by=self.user
        )
    
    def test_list_tasks(self):
        """Test listing tasks"""
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_task(self):
        """Test creating a task"""
        data = {
            'board': self.board.id,
            'title': 'New Task',
            'description': 'New Description',
            'status': 'to-do',
            'priority': 'high'
        }
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')
    
    def test_retrieve_task(self):
        """Test retrieving a single task"""
        response = self.client.get(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task')
    
    def test_update_task(self):
        """Test updating a task"""
        data = {
            'board': self.board.id,
            'title': 'Updated Task',
            'status': 'in-progress',
            'priority': 'high'
        }
        response = self.client.put(f'/api/tasks/{self.task.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Task')
    
    def test_delete_task(self):
        """Test deleting a task"""
        response = self.client.delete(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)


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
        
        self.board = Board.objects.create(
            title='Test Board',
            owner=self.user
        )
        self.task = Task.objects.create(
            board=self.board,
            title='Test Task',
            created_by=self.user
        )
        self.comment = Comment.objects.create(
            task=self.task,
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
        data = {
            'task': self.task.id,
            'content': 'New Comment'
        }
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
        self.task = Task.objects.create(
            board=self.board,
            title='Assigned Task',
            status='to-do',
            created_by=self.user
        )
        self.task.assigned_to.add(self.user)

        self.other_task = Task.objects.create(
            board=self.board,
            title='Other Task',
            status='todo',
            created_by=self.user
        )

    def test_assigned_to_me(self):
        """Test getting tasks assigned to current user"""
        response = self.client.get('/api/tasks/assigned-to-me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Assigned Task')

    def test_assigned_to_me_unauthorized(self):
        """Test that unauthenticated users cannot access"""
        self.client.credentials()
        response = self.client.get('/api/tasks/assigned-to-me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewingTasksAPITest(TestCase):
    """Test reviewing tasks endpoint"""

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
        self.reviewing_task = Task.objects.create(
            board=self.board,
            title='Reviewing Task',
            status='review',
            created_by=self.user
        )
        self.todo_task = Task.objects.create(
            board=self.board,
            title='Todo Task',
            status='todo',
            created_by=self.user
        )

    def test_reviewing_tasks(self):
        """Test getting tasks with reviewing status"""
        response = self.client.get('/api/tasks/reviewing/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Reviewing Task')

    def test_reviewing_tasks_unauthorized(self):
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
    """Test nested comment actions within TaskViewSet"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.board = Board.objects.create(title='Test Board', owner=self.user)
        self.task = Task.objects.create(board=self.board, title='Test Task', created_by=self.user)
        self.comment = Comment.objects.create(task=self.task, author=self.user, text='Old Comment')

    def test_nested_list_comments(self):
        """Test GET /api/tasks/<id>/comments/"""
        url = f'/api/tasks/{self.task.id}/comments/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_nested_create_comment(self):
        """Test POST /api/tasks/<id>/comments/"""
        url = f'/api/tasks/{self.task.id}/comments/'
        data = {'content': 'New Nested Comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'New Nested Comment')

    def test_nested_delete_comment(self):
        """Test DELETE /api/tasks/<id>/comments/<id>/"""
        url = f'/api/tasks/{self.task.id}/comments/{self.comment.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_nested_delete_comment_not_found(self):
        """Test DELETE nested comment with non-existent id"""
        url = f'/api/tasks/{self.task.id}/comments/999/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nested_delete_comment_unauthorized(self):
        """Test that other users cannot delete someone else's comment"""
        other_user = User.objects.create_user(username='other', password='password')
        other_token = Token.objects.create(user=other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {other_token.key}')
        
        url = f'/api/tasks/{self.task.id}/comments/{self.comment.id}/'
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
        user = User.objects.create_user(username='firstuser', password='password', first_name='John')
        from kanban_app.api.serializers import UserSerializer
        fullname = UserSerializer().get_fullname(user)
        self.assertEqual(fullname, 'John John')

    def test_user_serializer_fullname_only_last(self):
        """Test get_fullname with only last_name set"""
        user = User.objects.create_user(username='lastuser', password='password', last_name='Doe')
        from kanban_app.api.serializers import UserSerializer
        fullname = UserSerializer().get_fullname(user)
        self.assertEqual(fullname, 'Doe Doe')