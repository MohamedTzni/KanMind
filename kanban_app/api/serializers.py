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