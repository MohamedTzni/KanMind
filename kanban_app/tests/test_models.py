from django.contrib.auth.models import User
from django.test import TestCase

from kanban_app.models import Board, Ticket, Comment, Subticket


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
            description='Test Description',
            owner=self.user
        )
    
    def test_board_creation(self):
        """Test board is created correctly"""
        self.assertEqual(self.board.title, 'Test Board')
        self.assertEqual(self.board.description, 'Test Description')
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


class TicketModelTest(TestCase):
    """Test Ticket model"""
    
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
        self.ticket = Ticket.objects.create(
            board=self.board,
            title='Test Ticket',
            description='Test Description',
            status='to-do',
            priority='medium',
            created_by=self.user
        )
    
    def test_ticket_creation(self):
        """Test ticket is created correctly"""
        self.assertEqual(self.ticket.title, 'Test Ticket')
        self.assertEqual(self.ticket.board, self.board)
        self.assertEqual(self.ticket.status, 'to-do')
        self.assertEqual(self.ticket.priority, 'medium')
    
    def test_ticket_str(self):
        """Test ticket string representation"""
        self.assertEqual(str(self.ticket), 'Test Ticket')
    
    def test_ticket_status_choices(self):
        """Test ticket status choices"""
        self.ticket.status = 'in-progress'
        self.ticket.save()
        self.assertEqual(self.ticket.status, 'in-progress')
    
    def test_ticket_assigned_to(self):
        """Test assigning users to ticket"""
        user2 = User.objects.create_user(username='user2')
        self.ticket.assigned_to.add(user2)
        self.assertEqual(self.ticket.assigned_to.count(), 1)


class SubticketModelTest(TestCase):
    """Test Subticket model"""
    def setUp(self):
        self.user = User.objects.create_user(username='test')
        self.board = Board.objects.create(title='B', owner=self.user)
        self.ticket = Ticket.objects.create(board=self.board, title='T', created_by=self.user)
        self.subticket = Subticket.objects.create(ticket=self.ticket, title='S')

    def test_subticket_creation(self):
        self.assertEqual(self.subticket.title, 'S')
        self.assertEqual(self.subticket.ticket, self.ticket)
        self.assertFalse(self.subticket.done)


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
    
    def test_comment_creation(self):
        """Test comment is created correctly"""
        self.assertEqual(self.comment.text, 'Test Comment')
        self.assertEqual(self.comment.ticket, self.ticket)
        self.assertEqual(self.comment.author, self.user)
    
    def test_comment_str(self):
        """Test comment string representation"""
        expected = f"Comment by {self.user.username}"
        self.assertEqual(str(self.comment), expected)
