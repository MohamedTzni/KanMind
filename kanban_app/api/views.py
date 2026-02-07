from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from kanban_app.models import Board, Task, Comment
from kanban_app.api.serializers import BoardSerializer, TaskSerializer, CommentSerializer, UserSerializer
from kanban_app.api.permissions import IsOwner, IsOwnerOrMember


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        user = self.request.user
        owned = Board.objects.filter(owner=user)
        member = Board.objects.filter(members=user)
        return owned | member

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user
        owned_boards = Board.objects.filter(owner=user)
        member_boards = Board.objects.filter(members=user)
        all_boards = owned_boards | member_boards
        return Task.objects.filter(board__in=all_boards)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user
        owned_boards = Board.objects.filter(owner=user)
        member_boards = Board.objects.filter(members=user)
        all_boards = owned_boards | member_boards
        user_tasks = Task.objects.filter(board__in=all_boards)
        return Comment.objects.filter(task__in=user_tasks)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]