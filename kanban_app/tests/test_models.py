from django.contrib.auth.models import User
from django.test import TestCase

from kanban_app.models import Board, Task, Comment


class BoardModelTest(TestCase):
    """Test Board model"""
    
    def setUp(self):
        """Create test user and board"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.board = Board.objects.create(
            title='Test Board',
            owner=self.user
        )
    
    def test_board_creation(self):
        """Test board is created correctly"""
        self.assertEqual(self.board.title, 'Test Board')
        self.assertEqual(self.board.owner, self.user)
    
    def test_board_str(self):
        """Test board string representation"""
        self.assertEqual(str(self.board), 'Test Board')
    
    def test_board_members(self):
        """Test adding members to board"""
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com'
        )
        self.board.members.add(user2)
        self.assertEqual(self.board.members.count(), 1)
        self.assertIn(user2, self.board.members.all())


class TaskModelTest(TestCase):
    """Test Task model"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.board = Board.objects.create(
            title='Test Board',
            owner=self.user
        )
        self.task = Task.objects.create(
            board=self.board,
            title='Test Task',
            description='Test Description',
            status='todo',
            priority='medium',
            created_by=self.user
        )
    
    def test_task_creation(self):
        """Test task is created correctly"""
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.board, self.board)
        self.assertEqual(self.task.status, 'todo')
        self.assertEqual(self.task.priority, 'medium')
    
    def test_task_str(self):
        """Test task string representation"""
        self.assertEqual(str(self.task), 'Test Task')
    
    def test_task_status_choices(self):
        """Test task status choices"""
        self.task.status = 'in_progress'
        self.task.save()
        self.assertEqual(self.task.status, 'in_progress')
    
    def test_task_assigned_to(self):
        """Test assigning users to task"""
        user2 = User.objects.create_user(username='user2')
        self.task.assigned_to.add(user2)
        self.assertEqual(self.task.assigned_to.count(), 1)


class CommentModelTest(TestCase):
    """Test Comment model"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
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
    
    def test_comment_creation(self):
        """Test comment is created correctly"""
        self.assertEqual(self.comment.text, 'Test Comment')
        self.assertEqual(self.comment.task, self.task)
        self.assertEqual(self.comment.author, self.user)
    
    def test_comment_str(self):
        """Test comment string representation"""
        expected = f"Comment by {self.user.username}"
        self.assertEqual(str(self.comment), expected)