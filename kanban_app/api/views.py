from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kanban_app.api.permissions import IsBoardMember, IsOwner, IsOwnerOrMember
from kanban_app.api.serializers import (
    BoardListSerializer, BoardDetailSerializer,
    TicketSerializer, CommentSerializer, UserSerializer,
    UserListSerializer, SubticketSerializer,
)
from kanban_app.models import Board, Ticket, Comment, Subticket


class BoardListCreateView(generics.ListCreateAPIView):
    """View for listing and creating boards."""
    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        """Return boards where the user is an owner or member."""
        user = self.request.user
        if user.is_superuser:
            return Board.objects.all()
        owned = Board.objects.filter(owner=user)
        member = Board.objects.filter(members=user)
        return (owned | member).distinct()

    def perform_create(self, serializer):
        """Assign the requesting user as the board owner."""
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieve, update and delete of a single board."""
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        """Return only boards the user can access."""
        user = self.request.user
        owned = Board.objects.filter(owner=user)
        member = Board.objects.filter(members=user)
        return (owned | member).distinct()

    def _build_owner_data(self, owner):
        """Build owner data dict for PATCH response."""
        return {
            "id": owner.id,
            "email": owner.email,
            "fullname": UserSerializer().get_fullname(owner),
        }

    def _build_patch_response(self, instance):
        """Build PATCH response with owner_data and members_data."""
        return {
            "id": instance.id,
            "title": instance.title,
            "owner_data": self._build_owner_data(instance.owner),
            "members_data": UserSerializer(instance.members.all(), many=True).data,
        }

    def destroy(self, request, *args, **kwargs):
        """Only the board owner can delete."""
        instance = self.get_object()
        if instance.owner != request.user:
            return Response(
                {"detail": "Only the board owner can delete this board."},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        """Update board and return PATCH-specific response format."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(self._build_patch_response(instance))


class TicketViewSet(viewsets.ModelViewSet):
    """CRUD for tickets."""
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]

    def get_queryset(self):
        """Return filtered tickets for list, all tickets for detail actions."""
        if self.action == 'list':
            user = self.request.user
            all_boards = (
                Board.objects.filter(owner=user) | Board.objects.filter(members=user)
            )
            return Ticket.objects.filter(board__in=all_boards)
        return Ticket.objects.all()

    def _check_board_access(self, board_id, user):
        """Return error Response if board not found or user is not a member."""
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
        """Check board membership before creating a ticket."""
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
        """Build user dict for ticket response."""
        if not user:
            return None
        return {"id": user.id, "email": user.email, "fullname": UserSerializer().get_fullname(user)}

    def _ticket_response(self, instance):
        """Build a response with only the fields required by the API spec."""
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
        """Update a ticket and return only spec-required fields."""
        if 'board' in request.data:
            return Response(
                {"detail": "Changing the board is not allowed."},
                status=status.HTTP_403_FORBIDDEN,
            )
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
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
        """Set the current user as ticket creator."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Route to list or create comments for a ticket."""
        ticket = self.get_object()
        if request.method == 'GET':
            return self.list_comments(ticket)
        return self.create_comment(request, ticket)

    def list_comments(self, ticket):
        """Return all comments for a ticket."""
        data = [
            {
                "id": c.id,
                "created_at": c.created_at,
                "author": UserSerializer().get_fullname(c.author),
                "content": c.text,
            }
            for c in ticket.comments.all()
        ]
        return Response(data)

    def create_comment(self, request, ticket):
        """Create a new comment for a ticket."""
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
        """Fetch ticket and comment, return error Response on failure."""
        try:
            ticket = Ticket.objects.get(pk=ticket_id)
            return ticket, ticket.comments.get(pk=comment_id)
        except (Ticket.DoesNotExist, Comment.DoesNotExist):
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND), None

    def _check_comment_delete_permission(self, user, ticket, comment):
        """Return error Response if user lacks permission to delete, else None."""
        board = ticket.board
        if board.owner != user and user not in board.members.all():
            return Response(
                {"detail": "You must be a member of the board."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if comment.author != user:
            return Response(
                {"detail": "You can only delete your own comments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def delete_comment(self, request, ticket_id=None, comment_id=None):
        """Delete a specific comment of a ticket."""
        ticket, comment = self._get_ticket_and_comment(ticket_id, comment_id)
        if isinstance(ticket, Response):
            return ticket
        error = self._check_comment_delete_permission(request.user, ticket, comment)
        if error:
            return error
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubticketViewSet(viewsets.ModelViewSet):
    """CRUD for subtickets."""
    queryset = Subticket.objects.all()
    serializer_class = SubticketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return subtickets for accessible tickets."""
        user = self.request.user
        all_boards = (
            Board.objects.filter(owner=user) | Board.objects.filter(members=user)
        )
        return Subticket.objects.filter(ticket__board__in=all_boards)


class AssignedToMeView(APIView):
    """Return tickets assigned to the current user as assignee or reviewer."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return tickets where the user is the assignee or reviewer."""
        user = request.user
        all_boards = (
            Board.objects.filter(owner=user) | Board.objects.filter(members=user)
        )
        tickets = Ticket.objects.filter(
            board__in=all_boards
        ).filter(Q(assignee=user) | Q(reviewer=user))
        data = [
            {
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
            for t in tickets
        ]
        return Response(data)

    def _build_user_data(self, user):
        """Build user dict for ticket response."""
        if not user:
            return None
        return {"id": user.id, "email": user.email, "fullname": UserSerializer().get_fullname(user)}


class ReviewingTasksView(APIView):
    """Return tickets with status 'review' from the user's boards."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return tickets with status review from accessible boards."""
        user = request.user
        all_boards = (
            Board.objects.filter(owner=user) | Board.objects.filter(members=user)
        )
        tickets = Ticket.objects.filter(board__in=all_boards, reviewer=user)
        data = [
            {
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
            for t in tickets
        ]
        return Response(data)

    def _build_user_data(self, user):
        """Build user dict for ticket response."""
        if not user:
            return None
        return {"id": user.id, "email": user.email, "fullname": UserSerializer().get_fullname(user)}


class CommentViewSet(viewsets.ModelViewSet):
    """CRUD for comments."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """Return comments from tickets on accessible boards."""
        user = self.request.user
        all_boards = (
            Board.objects.filter(owner=user) | Board.objects.filter(members=user)
        )
        user_tickets = Ticket.objects.filter(board__in=all_boards)
        return Comment.objects.filter(ticket__in=user_tickets)

    def create(self, request, *args, **kwargs):
        """Validate that ticket is provided for standalone comment creation."""
        if 'ticket' not in request.data:
            return Response(
                {"ticket": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Set the current user as comment author."""
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only list of users."""
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
