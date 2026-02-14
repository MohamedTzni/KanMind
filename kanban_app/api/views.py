from django.contrib.auth.models import User

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kanban_app.api.permissions import IsBoardMember, IsOwner, IsOwnerOrMember
from kanban_app.api.serializers import (
    BoardListSerializer, BoardDetailSerializer,
    TaskSerializer, CommentSerializer, UserSerializer,
)
from kanban_app.models import Board, Task, Comment


class BoardListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating boards.
    Supports GET for a filtered list and POST for creation.
    """
    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        """
        Filters boards where the user is an owner or a member.
        Only returns accessible boards for the current user.
        """
        user = self.request.user
        owned = Board.objects.filter(owner=user)
        member = Board.objects.filter(members=user)
        return (owned | member).distinct()

    def perform_create(self, serializer):
        """
        Custom save logic for new boards.
        Automatically assigns the requesting user as the board owner.
        """
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for individual board operations.
    Supports GET (retrieve), PUT/PATCH (update), and DELETE.
    """
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD for tasks."""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]

    def get_queryset(self):
        """Return filtered tasks for list, all tasks for detail actions."""
        if self.action == 'list':
            user = self.request.user
            owned_boards = Board.objects.filter(owner=user)
            member_boards = Board.objects.filter(members=user)
            all_boards = owned_boards | member_boards
            return Task.objects.filter(board__in=all_boards)
        return Task.objects.all()

    def create(self, request, *args, **kwargs):
        """Check board membership before creating a task."""
        board_id = request.data.get('board')
        if not board_id:
            return Response(
                {"board": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            return Response(
                {"detail": "Board not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user = request.user
        if board.owner != user and user not in board.members.all():
            return Response(
                {"detail": "You must be a member of the board."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Set the current user as task creator."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Route to list or create comments for a task."""
        task = self.get_object()
        if request.method == 'GET':
            return self.list_comments(task)
        return self.create_comment(request, task)

    def list_comments(self, task):
        """Return all comments for a task."""
        comments = task.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def create_comment(self, request, task):
        """Create a new comment for a task."""
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, author=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete_comment(self, request, task_id=None, comment_id=None):
        """Delete a specific comment of a task."""
        try:
            task = Task.objects.get(pk=task_id)
            comment = task.comments.get(pk=comment_id)
        except (Task.DoesNotExist, Comment.DoesNotExist):
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        board = task.board
        if board.owner != request.user and request.user not in board.members.all():
            return Response(
                {"detail": "You must be a member of the board."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if comment.author != request.user:
            return Response(
                {"detail": "You can only delete your own comments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignedToMeView(APIView):
    """Return tasks assigned to the current user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return tasks where the user is in assigned_to."""
        user = request.user
        owned_boards = Board.objects.filter(owner=user)
        member_boards = Board.objects.filter(members=user)
        all_boards = owned_boards | member_boards
        tasks = Task.objects.filter(
            board__in=all_boards,
            assigned_to=user,
        )
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class ReviewingTasksView(APIView):
    """Return tasks with status review."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return review tasks from accessible boards."""
        user = request.user
        owned_boards = Board.objects.filter(owner=user)
        member_boards = Board.objects.filter(members=user)
        all_boards = owned_boards | member_boards
        tasks = Task.objects.filter(
            board__in=all_boards,
            status='review',
        )
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """CRUD for comments."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """Return comments from tasks on accessible boards."""
        user = self.request.user
        owned_boards = Board.objects.filter(owner=user)
        member_boards = Board.objects.filter(members=user)
        all_boards = owned_boards | member_boards
        user_tasks = Task.objects.filter(board__in=all_boards)
        return Comment.objects.filter(task__in=user_tasks)

    def create(self, request, *args, **kwargs):
        """Validate that task is provided for standalone comment creation."""
        if 'task' not in request.data:
            return Response(
                {"task": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Set the current user as comment author."""
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only list of users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
