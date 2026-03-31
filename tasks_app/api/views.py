from django.contrib.auth.models import User
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import UserSerializer, UserListSerializer
from boards_app.models import Board
from tasks_app.api.permissions import IsBoardMember, IsOwner
from tasks_app.api.serializers import (
    TicketSerializer, CommentSerializer, SubticketSerializer,
)
from tasks_app.models import Ticket, Comment, Subticket


class TicketViewSet(viewsets.ModelViewSet):
    """CRUD for tickets."""
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated()]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        if self.action == 'list':
            user = self.request.user
            all_boards = (
                Board.objects.filter(owner=user) | Board.objects.filter(members=user)
            )
            return Ticket.objects.filter(board__in=all_boards)
        return Ticket.objects.all()

    def _check_board_access(self, board_id, user):
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            return Response({"detail": "Board not found."}, status=status.HTTP_404_NOT_FOUND)
        if board.owner != user and user not in board.members.all():
            return Response(
                {"detail": "You must be a member of the board."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def create(self, request, *args, **kwargs):
        board_id = request.data.get('board')
        if not board_id:
            return Response({"board": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        error = self._check_board_access(board_id, request.user)
        if error:
            return error
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(self._ticket_response(serializer.instance), status=status.HTTP_201_CREATED)

    def _build_user_data(self, user):
        if not user:
            return None
        return {"id": user.id, "email": user.email, "fullname": UserSerializer().get_fullname(user)}

    def _ticket_response(self, instance):
        return {
            "id": instance.id,
            "board": instance.board_id,
            "title": instance.title,
            "description": instance.description,
            "status": instance.status,
            "priority": instance.priority,
            "assignee": self._build_user_data(instance.assignee),
            "reviewer": self._build_user_data(instance.reviewer),
            "due_date": str(instance.due_date) if instance.due_date else None,
            "comments_count": instance.comments.count(),
        }

    def update(self, request, *args, **kwargs):
        if 'board' in request.data:
            return Response(
                {"detail": "Changing the board is not allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.refresh_from_db()
        return Response({
            "id": instance.id,
            "title": instance.title,
            "description": instance.description,
            "status": instance.status,
            "priority": instance.priority,
            "assignee": self._build_user_data(instance.assignee),
            "reviewer": self._build_user_data(instance.reviewer),
            "due_date": str(instance.due_date) if instance.due_date else None,
        })

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        ticket = self.get_object()
        if request.method == 'GET':
            return self._list_comments(ticket)
        return self._create_comment(request, ticket)

    def _list_comments(self, ticket):
        data = [
            {
                "id": c.id,
                "created_at": c.created_at,
                "author": UserSerializer().get_fullname(c.author),
                "content": c.text,
            }
            for c in ticket.comments.order_by('created_at')
        ]
        return Response(data)

    def _create_comment(self, request, ticket):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(ticket=ticket, author=request.user)
            return Response(
                {
                    "id": comment.id,
                    "created_at": comment.created_at,
                    "author": UserSerializer().get_fullname(comment.author),
                    "content": comment.text,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_ticket_and_comment(self, ticket_id, comment_id):
        try:
            ticket = Ticket.objects.get(pk=ticket_id)
            return ticket, ticket.comments.get(pk=comment_id)
        except (Ticket.DoesNotExist, Comment.DoesNotExist):
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND), None

    def _check_comment_delete_permission(self, user, ticket, comment):
        if comment.author != user:
            return Response(
                {"detail": "You can only delete your own comments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def delete_comment(self, request, ticket_id=None, comment_id=None):
        ticket, comment = self._get_ticket_and_comment(ticket_id, comment_id)
        if isinstance(ticket, Response):
            return ticket
        error = self._check_comment_delete_permission(request.user, ticket, comment)
        if error:
            return error
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        board_owner = instance.board.owner
        is_creator = instance.created_by == request.user
        is_board_owner = board_owner == request.user

        if not (is_creator or is_board_owner):
            return Response(
                {"detail": "Only the task creator or board owner can delete this task."},
                status=status.HTTP_403_FORBIDDEN,
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubticketViewSet(viewsets.ModelViewSet):
    """CRUD for subtickets."""
    queryset = Subticket.objects.all()
    serializer_class = SubticketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        all_boards = (
            Board.objects.filter(owner=user) | Board.objects.filter(members=user)
        )
        return Subticket.objects.filter(ticket__board__in=all_boards)


class AssignedToMeView(APIView):
    """Return tickets assigned to the current user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        all_boards = (
            Board.objects.filter(owner=user) | Board.objects.filter(members=user)
        )
        tickets = Ticket.objects.filter(
            board__in=all_boards,
            assignee=user,
        )
        data = [self._ticket_data(t) for t in tickets]
        return Response(data)

    def _build_user_data(self, user):
        if not user:
            return None
        return {"id": user.id, "email": user.email, "fullname": UserSerializer().get_fullname(user)}

    def _ticket_data(self, t):
        return {
            "id": t.id,
            "board": t.board_id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "assignee": self._build_user_data(t.assignee),
            "reviewer": self._build_user_data(t.reviewer),
            "due_date": str(t.due_date) if t.due_date else None,
            "comments_count": t.comments.count(),
        }


class ReviewingTasksView(APIView):
    """Return tickets where the current user is set as reviewer."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        all_boards = (
            Board.objects.filter(owner=user) | Board.objects.filter(members=user)
        )
        tickets = Ticket.objects.filter(board__in=all_boards, reviewer=user)
        data = [self._ticket_data(t) for t in tickets]
        return Response(data)

    def _build_user_data(self, user):
        if not user:
            return None
        return {"id": user.id, "email": user.email, "fullname": UserSerializer().get_fullname(user)}

    def _ticket_data(self, t):
        return {
            "id": t.id,
            "board": t.board_id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "assignee": self._build_user_data(t.assignee),
            "reviewer": self._build_user_data(t.reviewer),
            "due_date": str(t.due_date) if t.due_date else None,
            "comments_count": t.comments.count(),
        }


class CommentViewSet(viewsets.ModelViewSet):
    """CRUD for comments."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user
        all_boards = (
            Board.objects.filter(owner=user) | Board.objects.filter(members=user)
        )
        user_tickets = Ticket.objects.filter(board__in=all_boards)
        return Comment.objects.filter(ticket__in=user_tickets)

    def create(self, request, *args, **kwargs):
        if 'ticket' not in request.data:
            return Response(
                {"ticket": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only list of users."""
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
