from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

from kanban_app.models import Board, Task, Comment
from kanban_app.api.serializers import (
    BoardSerializer,
    TaskSerializer,
    CommentSerializer,
    UserSerializer
)


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Board model.
    Provides CRUD operations for boards.
    """
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter boards to show only boards where user is owner or member.
        """
        user = self.request.user
        return Board.objects.filter(owner=user) | Board.objects.filter(members=user)

    def perform_create(self, serializer):
        """
        Set the owner to the current user when creating a board.
        """
        serializer.save(owner=self.request.user)