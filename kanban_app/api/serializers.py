from django.contrib.auth.models import User

from rest_framework import serializers

from kanban_app.models import Board, Task, Comment


class BoardSerializer(serializers.ModelSerializer):
    """Serializer for Board model."""
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'owner', 'members',
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
        return obj.tasks.filter(status='todo').count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of high priority tasks."""
        return obj.tasks.filter(priority='high').count()


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""
    comments_count = serializers.SerializerMethodField()
    assignee = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description',
            'status', 'priority', 'assigned_to',
            'created_by', 'created_at', 'updated_at',
            'due_date', 'comments_count', 'assignee',
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at',
        ]

    def get_comments_count(self, obj):
        """Return the number of comments on this task."""
        return obj.comments.count()

    def get_assignee(self, obj):
        """Return the first assigned user or None."""
        user = obj.assigned_to.first()
        if user is None:
            return None
        fullname = f"{user.first_name} {user.last_name}"
        return {
            'id': user.id,
            'fullname': fullname.strip(),
        }


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""
    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'text', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
