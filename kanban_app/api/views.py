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

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task model.
    Provides CRUD operations for tasks.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter tasks to show only tasks from boards where user is owner or member.
        """
        user = self.request.user
        user_boards = Board.objects.filter(owner=user) | Board.objects.filter(members=user)
        return Task.objects.filter(board__in=user_boards)

    def perform_create(self, serializer):
        """
        Set the created_by to the current user when creating a task.
        """
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def assigned_to_me(self, request):
        """
        Custom endpoint: GET /api/tasks/assigned-to-me/
        Returns all tasks assigned to the current user.
        """
        user = request.user
        tasks = Task.objects.filter(assigned_to=user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def reviewing(self, request):
        """
        Custom endpoint: GET /api/tasks/reviewing/
        Returns all tasks with status 'reviewing'.
        """
        user = request.user
        user_boards = Board.objects.filter(owner=user) | Board.objects.filter(members=user)
        tasks = Task.objects.filter(board__in=user_boards, status='reviewing')
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)