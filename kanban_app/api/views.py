from django.contrib.auth.models import User

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kanban_app.api.permissions import IsOwner, IsOwnerOrMember
from kanban_app.api.serializers import (
    BoardSerializer, TaskSerializer,
    CommentSerializer, UserSerializer,
)
from kanban_app.models import Board, Task, Comment


class BoardViewSet(viewsets.ModelViewSet):
    """CRUD for boards."""
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        user = self.request.user
        owned = Board.objects.filter(owner=user)
        member = Board.objects.filter(members=user)
        return (owned | member).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD for tasks."""
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

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Handle comments for a specific task."""
        task = self.get_object()
        
        if request.method == 'GET':
            # Get all comments for this task
            comments = task.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
            
        elif request.method == 'POST':
            # Create a new comment for this task
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(task=task, author=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_comment(self, request, task_id=None, comment_id=None):
        """Löscht einen spezifischen Kommentar eines Tasks."""
        try:
            # Wir suchen erst den Task und dann den Kommentar darin
            task = Task.objects.get(pk=task_id)
            comment = task.comments.get(pk=comment_id)
        except (Task.DoesNotExist, Comment.DoesNotExist):
            return Response({"error": "Nicht gefunden"}, status=status.HTTP_404_NOT_FOUND)

        # Sicherheit: Nur der Ersteller (author) darf seinen Kommentar löschen
        if comment.author != request.user:
            return Response({"error": "Nicht erlaubt!"}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignedToMeView(APIView):
    """Return tasks assigned to the current user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        owned_boards = Board.objects.filter(owner=user)
        member_boards = Board.objects.filter(members=user)
        all_boards = owned_boards | member_boards
        tasks = Task.objects.filter(board__in=all_boards, assigned_to=user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class ReviewingTasksView(APIView):
    """Return tasks with status review."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        owned_boards = Board.objects.filter(owner=user)
        member_boards = Board.objects.filter(members=user)
        all_boards = owned_boards | member_boards
        tasks = Task.objects.filter(board__in=all_boards, status='review')
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """CRUD for comments."""
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
    """Read-only list of users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]