from django.contrib.auth.models import User

from rest_framework import serializers

from kanban_app.models import Board, Task, Comment


class BoardSerializer(serializers.ModelSerializer):
    """Serializer for Board model."""
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""
    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assigned_to',
            'created_by',
            'created_at',
            'updated_at',
            'due_date',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


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
