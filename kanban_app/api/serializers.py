from django.contrib.auth.models import User
from rest_framework import serializers
from kanban_app.models import Board, Ticket, Comment, Subticket


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


class SubticketSerializer(serializers.ModelSerializer):
    """Serializer for Subticket model."""
    class Meta:
        model = Subticket
        fields = ['id', 'title', 'done', 'ticket']
        read_only_fields = ['id']


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
        """Meta options for TicketSerializer."""
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
        """Return the number of comments on this ticket."""
        return obj.comments.count()


class TicketNestedSerializer(serializers.ModelSerializer):
    """Slim ticket serializer for nested display in board detail."""
    comments_count = serializers.SerializerMethodField()
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    assigned_to = UserSerializer(many=True, read_only=True)

    class Meta:
        """Meta options for TicketNestedSerializer."""
        model = Ticket
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'assigned_to',
            'due_date', 'comments_count',
        ]

    def get_comments_count(self, obj):
        """Return the number of comments on this ticket."""
        return obj.comments.count()


class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for the Board list view.
    Provides a summary of the board including various counts.
    """
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'description', 'owner', 'members']
        read_only_fields = ['id', 'owner']

    def to_representation(self, instance):
        """
        Returns the data in the format required for the list overview.
        Includes membership and ticket statistics.
        """
        return {
            "id": instance.id,
            "title": instance.title,
            "description": instance.description,
            "member_count": instance.members.count(),
            "ticket_count": instance.tickets.count(),
            "tasks_to_do_count": instance.tickets.filter(status='to-do').count(),
            "tasks_high_prio_count": instance.tickets.filter(priority='high').count(),
            "owner_id": instance.owner_id,
        }


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the Board detail and update view.
    Provides full user objects for owners and members.
    """

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'description', 'owner', 'members']
        read_only_fields = ['id', 'owner']

    def to_representation(self, instance):
        """
        Returns full detail representation.
        Includes owner_id, members as user objects, and nested tickets.
        """
        return {
            "id": instance.id,
            "title": instance.title,
            "description": instance.description,
            "owner_id": instance.owner_id,
            "members": UserSerializer(instance.members.all(), many=True).data,
            "tickets": TicketNestedSerializer(instance.tickets.all(), many=True).data,
        }


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""
    author = serializers.SerializerMethodField()

    # The frontend sends 'content', but the model uses 'text'.
    content = serializers.CharField(source='text')

    class Meta:
        """Meta options for CommentSerializer."""
        model = Comment
        fields = [
            'id', 'ticket', 'author', 'text',
            'content', 'created_at',
        ]
        read_only_fields = [
            'id', 'author', 'text', 'created_at',
        ]
        extra_kwargs = {
            'ticket': {'required': False}
        }

    def get_author(self, obj):
        """Return the author full name as a string."""
        return UserSerializer().get_fullname(obj.author)
