from rest_framework import serializers
from django.contrib.auth.models import User
from kanban_app.models import Board, Task, Comment


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for Board model.
    Provides additional computed fields for counts.
    """
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'members',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_member_count(self, obj):
        """Returns the number of members in the board."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Returns the total number of tasks in the board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Returns the number of tasks with 'todo' status."""
        return obj.tasks.filter(status='todo').count()

    def get_tasks_high_prio_count(self, obj):
        """Returns the number of high priority tasks."""
        return obj.tasks.filter(priority='high').count()


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model.
    Includes board and assigned users information.
    """
    board_id = serializers.IntegerField(source='board.id', read_only=True)
    created_by_id = serializers.IntegerField(source='created_by.id', read_only=True, allow_null=True)
    assigned_to_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        source='assigned_to',
        required=False
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'board_id',
            'title',
            'description',
            'status',
            'priority',
            'assigned_to_ids',
            'created_by_id',
            'created_at',
            'updated_at',
            'due_date',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_id']


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    Includes author information.
    """
    author_id = serializers.IntegerField(source='author.id', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'task',
            'author_id',
            'author_name',
            'text',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'author_id', 'author_name']


class UserSerializer(serializers.ModelSerializer):
    """
    Basic serializer for User model.
    Used for user information display.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']