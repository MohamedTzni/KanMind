from django.contrib.auth.models import User
from rest_framework import serializers
from kanban_app.models import Board, Task, Comment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    fullname = serializers.SerializerMethodField()

    class Meta:
        """Meta options for UserSerializer."""
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, user):
        """Format user full name for the response."""
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
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        """Meta options for TaskSerializer."""
        model = Task
        fields = [
            'id', 'board', 'title', 'description',
            'status', 'priority',
            'assignee', 'reviewer',
            'assignee_id', 'reviewer_id',
            'due_date', 'comments_count',
        ]
        read_only_fields = ['id']

    def validate(self, data):
        """Check that assignee and reviewer are board members."""
        board = data.get('board') or getattr(self.instance, 'board', None)
        if not board:
            return data
        board_user_ids = set(board.members.values_list('id', flat=True))
        board_user_ids.add(board.owner_id)
        for field in ('assignee', 'reviewer'):
            user = data.get(field)
            if user and user.id not in board_user_ids:
                raise serializers.ValidationError(
                    {f"{field}_id": f"User must be a member of the board."}
                )
        return data

    def get_comments_count(self, obj):
        """Return the number of comments on this task."""
        return obj.comments.count()


class TaskNestedSerializer(serializers.ModelSerializer):
    """Slim task serializer for nested display in board detail."""
    comments_count = serializers.SerializerMethodField()
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)

    class Meta:
        """Meta options for TaskNestedSerializer."""
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count',
        ]

    def get_comments_count(self, obj):
        """Return the number of comments on this task."""
        return obj.comments.count()


class BoardCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a Board (POST /api/boards/)."""
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
    )
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        """Meta options for BoardCreateSerializer."""
        model = Board
        fields = [
            'id', 'title', 'member_count', 'ticket_count',
            'tasks_to_do_count', 'tasks_high_prio_count',
            'owner_id', 'members',
        ]
        read_only_fields = ['id', 'owner_id']

    def get_member_count(self, obj):
        """Return the number of board members."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the number of tasks on this board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks with status todo."""
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of high priority tasks."""
        return obj.tasks.filter(priority='high').count()

    def to_representation(self, instance):
        """Return only the summary fields (without members list)."""
        data = super().to_representation(instance)
        data.pop('members', None)
        return data


class BoardSerializer(serializers.ModelSerializer):
    """Serializer for Board detail view."""
    tasks = TaskNestedSerializer(many=True, read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        """Meta options for BoardSerializer."""
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
        read_only_fields = ['id', 'owner_id']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""
    author = serializers.SerializerMethodField()

    # The frontend sends 'content', but the model uses 'text'.
    content = serializers.CharField(source='text')

    class Meta:
        """Meta options for CommentSerializer."""
        model = Comment
        fields = [
            'id', 'task', 'author', 'text',
            'content', 'created_at',
        ]
        read_only_fields = [
            'id', 'author', 'text', 'created_at',
        ]
        extra_kwargs = {
            'task': {'required': False}
        }

    def get_author(self, obj):
        """Return the author full name as a string."""
        return UserSerializer().get_fullname(obj.author)
