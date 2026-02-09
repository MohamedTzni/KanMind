from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from kanban_app.models import Board, Task, Comment
from kanban_app.api.permissions import IsOwner, IsOwnerOrMember


class IsOwnerPermissionTest(TestCase):
    """Test IsOwner permission"""
    
    def setUp(self):
        """Create test data"""
        self.factory = APIRequestFactory()
        self.permission = IsOwner()
        self.user = User.objects.create_user(username='owner', password='pass')
        self.other_user = User.objects.create_user(username='other', password='pass')
        
        self.board = Board.objects.create(title='Test Board', owner=self.user)
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
    
    def test_safe_methods_allowed(self):
        """Test that safe methods (GET) are allowed"""
        request = self.factory.get('/')
        request.user = self.other_user
        
        # Should allow read for any authenticated user
        self.assertTrue(self.permission.has_object_permission(request, None, self.task))
    
    def test_owner_can_modify_task(self):
        """Test that owner can modify task (created_by)"""
        request = self.factory.put('/')
        request.user = self.user
        
        self.assertTrue(self.permission.has_object_permission(request, None, self.task))
    
    def test_non_owner_cannot_modify_task(self):
        """Test that non-owner cannot modify task"""
        request = self.factory.put('/')
        request.user = self.other_user
        
        self.assertFalse(self.permission.has_object_permission(request, None, self.task))
    
    def test_author_can_modify_comment(self):
        """Test that author can modify comment"""
        request = self.factory.put('/')
        request.user = self.user
        
        self.assertTrue(self.permission.has_object_permission(request, None, self.comment))
    
    def test_non_author_cannot_modify_comment(self):
        """Test that non-author cannot modify comment"""
        request = self.factory.put('/')
        request.user = self.other_user
        
        self.assertFalse(self.permission.has_object_permission(request, None, self.comment))


class IsOwnerOrMemberPermissionTest(TestCase):
    """Test IsOwnerOrMember permission"""
    
    def setUp(self):
        """Create test data"""
        self.factory = APIRequestFactory()
        self.permission = IsOwnerOrMember()
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.member = User.objects.create_user(username='member', password='pass')
        self.stranger = User.objects.create_user(username='stranger', password='pass')
        
        self.board = Board.objects.create(title='Test Board', owner=self.owner)
        self.board.members.add(self.member)
    
    def test_owner_has_permission(self):
        """Test that owner has permission"""
        request = self.factory.get('/')
        request.user = self.owner
        
        self.assertTrue(self.permission.has_object_permission(request, None, self.board))
    
    def test_member_has_permission(self):
        """Test that member has permission"""
        request = self.factory.get('/')
        request.user = self.member
        
        self.assertTrue(self.permission.has_object_permission(request, None, self.board))
    
    def test_stranger_no_permission(self):
        """Test that stranger has no permission"""
        request = self.factory.get('/')
        request.user = self.stranger
        
        self.assertFalse(self.permission.has_object_permission(request, None, self.board))


