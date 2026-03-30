from rest_framework import serializers
from django.contrib.auth.models import User

from auth_app.api.serializers import UserSerializer
from boards_app.models import Board


class BoardListSerializer(serializers.ModelSerializer):
    """Serializer for the Board list view."""
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
        return {
            "id": instance.id,
            "title": instance.title,
            "member_count": instance.members.count(),
            "ticket_count": instance.tickets.count(),
            "tasks_to_do_count": instance.tickets.filter(status='to-do').count(),
            "tasks_high_prio_count": instance.tickets.filter(priority='high').count(),
            "owner_id": instance.owner_id,
        }


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serializer for the Board detail and update view."""
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
        from tasks_app.api.serializers import TicketNestedSerializer
        return {
            "id": instance.id,
            "title": instance.title,
            "owner_id": instance.owner_id,
            "members": UserSerializer(instance.members.all(), many=True).data,
            "tasks": TicketNestedSerializer(instance.tickets.all(), many=True).data,
        }
