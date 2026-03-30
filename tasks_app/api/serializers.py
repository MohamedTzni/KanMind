from django.contrib.auth.models import User

from rest_framework import serializers

from auth_app.api.serializers import UserSerializer
from tasks_app.models import Ticket, Comment, Subticket


class SubticketSerializer(serializers.ModelSerializer):
    """Serializer for Subticket model."""
    class Meta:
        model = Subticket
        fields = ['id', 'title', 'done', 'ticket']
        read_only_fields = ['id']


class TicketNestedSerializer(serializers.ModelSerializer):
    """Slim ticket serializer for nested display in board detail."""
    comments_count = serializers.SerializerMethodField()
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count',
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


class TicketSerializer(serializers.ModelSerializer):
    """Serializer for Ticket model."""
    comments_count = serializers.SerializerMethodField()
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    assigned_to_data = UserSerializer(source='assigned_to', many=True, read_only=True)
    subtickets = SubticketSerializer(many=True, read_only=True)

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
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Ticket
        fields = [
            'id', 'board', 'title', 'description',
            'status', 'priority',
            'assignee', 'reviewer',
            'assignee_id', 'reviewer_id',
            'assigned_to', 'assigned_to_data',
            'due_date', 'comments_count', 'subtickets',
        ]
        read_only_fields = ['id']

    def validate(self, data):
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
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""
    author = serializers.SerializerMethodField()
    content = serializers.CharField(source='text')

    class Meta:
        model = Comment
        fields = ['id', 'ticket', 'author', 'text', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'text', 'created_at']
        extra_kwargs = {'ticket': {'required': False}}

    def get_author(self, obj):
        return UserSerializer().get_fullname(obj.author)
