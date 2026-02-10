from django.contrib.auth.models import User
from rest_framework import serializers
from kanban_app.models import Board, Task, Comment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'fullname']

    def get_fullname(self, user):
        """Helper to format user data for response - Beginner friendly version."""
        first = user.first_name.strip()
        last = user.last_name.strip()
        
        if not first and not last:
            return f"{user.username} {user.username}"
        if not last:
            return f"{first} {first}"
        if not first:
            return f"{last} {last}"
        
        return f"{first} {last}"


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""
    comments_count = serializers.SerializerMethodField()
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', write_only=True, required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description',
            'status', 'priority', 'assigned_to',
            'assignee', 'reviewer', 'assignee_id', 'reviewer_id',
            'created_by', 'created_at', 'updated_at',
            'due_date', 'comments_count',
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at',
        ]

    def get_comments_count(self, obj):
        """Return the number of comments on this task."""
        return obj.comments.count()


class BoardSerializer(serializers.ModelSerializer):
    """Serializer for Board model."""
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    
    # Nested fields for the frontend
    tasks = TaskSerializer(many=True, read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'owner', 'members', 'tasks',
            'created_at', 'updated_at',
            'member_count', 'ticket_count',
            'tasks_to_do_count', 'tasks_high_prio_count',
        ]
        read_only_fields = [
            'id', 'owner', 'created_at', 'updated_at',
        ]

    def get_member_count(self, obj):
        """Return the number of board members."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the number of tasks on this board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks with status todo."""
        # Using the new status string from the model
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of high priority tasks."""
        return obj.tasks.filter(priority='high').count()


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""
    author = UserSerializer(read_only=True)
    
    # Das Frontend schickt 'content', aber unser Modell nutzt 'text'.
    # Mit source='text' sagen wir Django, dass 'content' in 'text' gespeichert werden soll.
    content = serializers.CharField(source='text', write_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'text', 'content', 'created_at']
        read_only_fields = ['id', 'task', 'author', 'text', 'created_at']
